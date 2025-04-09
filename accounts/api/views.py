from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from accounts.models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import random
import string
import os
import threading
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from celery import shared_task
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from accounts.tasks import send_verification_email_task
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# email verification token send email


def send_email_verification_token(email):
    user = CustomUser.objects.get(email=email)
    user.send_email_verification_token()
    return Response({"message": "Email verification token sent"})


@shared_task
async def send_verification_email(email, verification_url):
    """Async email yuborish"""
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email
    message["Subject"] = "Email tasdiqlash"

    body = (
        f"Iltimos, hisobingizni tasdiqlash uchun quyidagi havolaga kiring: {verification_url}\n"
        f"Eslatma: Havola 5 daqiqa davomida amal qiladi."
    )
    message.attach(MIMEText(body, "plain"))

    try:
        smtp = aiosmtplib.SMTP(
            hostname=settings.EMAIL_HOST, port=settings.EMAIL_PORT, use_tls=True
        )
        await smtp.connect()
        await smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "post", "put", "delete"]
    
    def get_permissions(self):
        """
        Action ga qarab permission ni belgilash
        """
        if self.action in ['create', 'verify_email']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "email", "password", "password2"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                "password2": openapi.Schema(
                    type=openapi.TYPE_STRING, format="password"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Foydalanuvchi yaratildi",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Foydalanuvchini yaratish
            user = serializer.save(is_active=False)

            # Verification token yaratish
            verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            # Token ma'lumotlarini cache ga saqlash
            cache_key = f"email_verification_{verification_token}"
            cache.set(cache_key, {
                'user_id': user.id,
                'email': user.email,
                'timestamp': timezone.now().timestamp()
            }, timeout=300)  # 5 daqiqa

            # Verification URL
            verification_url = f"{settings.FRONTEND_URL}/accounts/api/users/verify-email/?token={verification_token}"

            # Email yuborish
            send_verification_email_task.delay(user.email, verification_url)

            return Response({
                'status': 'success',
                'message': 'Foydalanuvchi yaratildi. Email orqali tasdiqlash havolasi yuborildi.',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Xatolik yuz berganda foydalanuvchini o'chirish
            if 'user' in locals():
                user.delete()
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, 
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='verify-email',
        url_name='verify-email'
    )
    @method_decorator(csrf_exempt)
    def verify_email(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'status': 'error',
                'message': 'Token topilmadi.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cache dan token ma'lumotlarini olish
        cache_key = f"email_verification_{token}"
        cache_data = cache.get(cache_key)

        if not cache_data:
            return Response({
                'status': 'error',
                'message': 'Noto\'g\'ri yoki yaroqsiz token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=cache_data['user_id'])
            
            # Token muddati tekshirish (5 daqiqa)
            elapsed_time = timezone.now().timestamp() - cache_data['timestamp']
            if elapsed_time > 300:  # 5 daqiqa
                cache.delete(cache_key)
                if not user.is_active:
                    user.delete()
                return Response({
                    'status': 'error',
                    'message': 'Tasdiqlash muddati tugagan. Iltimos, qaytadan ro\'yxatdan o\'ting.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Foydalanuvchini aktivlashtirish
            user.is_active = True
            user.save()
            
            # Cache
            cache.delete(cache_key)

            return Response({
                'status': 'success',
                'message': 'Email muvaffaqiyatli tasdiqlandi.'
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Foydalanuvchi topilmadi.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # send email verification token
        email = request.data.get("email")
        user = CustomUser.objects.get(email=email)
        user.send_email_verification_token()
        return Response({"message": "Email verification token sent"})


class LogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout current user",
        responses={
            200: openapi.Response(
                description="Successfully logged out",
            ),
            401: "Unauthorized",
        },
    )
    def post(self, request):
        # Clear credentials
        request.auth = None
        logout(request)
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    """
    API endpoint for JWT token generation
    """

    @swagger_auto_schema(
        operation_description="Get JWT tokens with username and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: "Unauthorized",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
