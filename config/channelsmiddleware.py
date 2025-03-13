from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from urllib.parse import parse_qs
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user = User.objects.get(id=validated_token["user_id"])
        print(f"{user}")
        return user

    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        try:
            # Debug uchun
            print("WebSocket connection attempt")
            print("Scope:", scope)

            query_string = scope.get("query_string", b"").decode("utf8")
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]

            print(f"Token from query: {token}")  # Debug uchun

            if not token:
                print("Token not found in query string")
                scope["user"] = AnonymousUser()
                return await self.inner(scope, receive, send)

            try:
                # Token validatsiyasi
                UntypedToken(token)
                decoded_data = jwt_decode(
                    token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                print(f"Decoded token data: {decoded_data}")  # Debug uchun

                user = await get_user(validated_token=decoded_data)
                print(f"Retrieved user: {user}")  # Debug uchun

                scope["user"] = user
            except Exception as e:
                print(f"Token validation error: {str(e)}")
                scope["user"] = AnonymousUser()

        except Exception as e:
            print(f"Middleware error: {str(e)}")
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
