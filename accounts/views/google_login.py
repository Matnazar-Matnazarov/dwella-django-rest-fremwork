from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.settings import api_settings
import logging
import json
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

GOOGLE_CLIENT_ID = "322786648793-lahah2h86g0pgfe45ips0rua3tp1ngtv.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(APIView):
    """
    Custom view to handle Google login properly and respond to CORS preflight requests
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request, *args, **kwargs):
        try:
            # Log request
            logger.info(f"Google login request received at: {request.path}")
            print(f"Google login request headers: {request.headers}")
            print(f"Google login request body: {request.data}")
            
            # Set CORS headers for the actual response
            response_headers = {
                'Access-Control-Allow-Origin': request.headers.get('Origin', 'http://localhost:3000'),
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, Authorization',
                'Access-Control-Allow-Credentials': 'true',
            }
            
            # Check for token
            access_token = request.data.get('access_token')
            if not access_token:
                return Response(
                    {"detail": "Missing access_token"}, 
                    status=status.HTTP_400_BAD_REQUEST,
                    headers=response_headers
                )
            
            # Initialize adapter
            adapter = GoogleOAuth2Adapter(request)
            
            try:
                # Parse and validate token
                app = adapter.get_provider().get_app(request)
                token = adapter.parse_token({'access_token': access_token})
                token_user = adapter.get_user_info(adapter.get_access_token(token))
                social_email = token_user.get('email')
                
                print(f"Google user info: {token_user}")
                
                # Get or create user
                from allauth.account.models import EmailAddress
                from allauth.socialaccount.models import SocialAccount
                from django.contrib.auth import get_user_model
                
                User = get_user_model()
                
                try:
                    email_address = EmailAddress.objects.get(email=social_email)
                    user = email_address.user
                except EmailAddress.DoesNotExist:
                    # Create user if doesn't exist
                    if not User.objects.filter(email=social_email).exists():
                        user = User.objects.create_user(
                            username=social_email.split('@')[0],
                            email=social_email,
                            first_name=token_user.get('given_name', ''),
                            last_name=token_user.get('family_name', ''),
                            password=User.objects.make_random_password(),
                            is_active=True,
                            role='CLIENT'  # Default role
                        )
                        EmailAddress.objects.create(
                            user=user,
                            email=social_email,
                            primary=True,
                            verified=True
                        )
                    else:
                        user = User.objects.get(email=social_email)
                
                # Create or get social account
                try:
                    social_account = SocialAccount.objects.get(provider='google', user=user)
                except SocialAccount.DoesNotExist:
                    social_account = SocialAccount.objects.create(
                        provider='google',
                        user=user,
                        uid=token_user.get('id'),
                        extra_data=token_user
                    )
                
                # Generate JWT tokens
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                # Format user data
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'role': user.role,
                    'is_active': user.is_active,
                    'picture': request.build_absolute_uri(user.picture.url) if hasattr(user, 'picture') and user.picture else None,
                }
                
                # Format response
                formatted_response = {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': user_data
                }
                
                print(f"Google login successful for user: {user.email}")
                
                # Return response with CORS headers
                response = JsonResponse(formatted_response)
                for header, value in response_headers.items():
                    response[header] = value
                
                return response
                
            except Exception as e:
                logger.exception(f"Error in Google authentication: {str(e)}")
                print(f"Google login error: {str(e)}")
                
                response = JsonResponse(
                    {"detail": f"Google authentication failed: {str(e)}"},
                    status=400
                )
                
                for header, value in response_headers.items():
                    response[header] = value
                
                return response
            
        except Exception as e:
            logger.exception(f"Google login exception: {str(e)}")
            print(f"Google login exception: {str(e)}")
            
            response = JsonResponse(
                {"detail": f"Google login failed: {str(e)}"},
                status=500
            )
            
            response["Access-Control-Allow-Origin"] = request.headers.get('Origin', 'http://localhost:3000')
            response["Access-Control-Allow-Credentials"] = "true"
            
            return response
    
    def options(self, request, *args, **kwargs):
        """
        Handle preflight OPTIONS requests for CORS
        """
        print(f"OPTIONS request received at: {request.path}")
        print(f"OPTIONS request headers: {request.headers}")
        
        response = JsonResponse({})
        
        response["Access-Control-Allow-Origin"] = request.headers.get('Origin', 'http://localhost:3000')
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, Authorization"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"  # 24 hours
        
        return response