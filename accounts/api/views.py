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
from django.core.mail import send_mail
import random
import string
import os
import threading
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.conf import settings
import time
from django.core.cache import cache
from celery import shared_task
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from accounts.tasks import send_verification_email_task

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
        if self.action == "create" or self.action == "verify_email":
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
            return Response(serializer.errors, status=400)

        try:
            # Foydalanuvchini yaratish
            user = serializer.save(is_active=False)

            # Verification token yaratish
            verification_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=32)
            )

            # Token va timestamp ni Redis-cache ga saqlash
            cache_key = f"email_verification_{verification_token}"
            cache_data = {"user_id": user.id, "timestamp": timezone.now().timestamp()}
            # 5 daqiqalik TTL bilan saqlash
            cache.set(cache_key, cache_data, timeout=300)

            # Email yuborish
            # Backend URL ni ishlatamiz, chunki verify-email endpointi backend da
            verification_url = f"{settings.FRONTEND_URL}/accounts/api/users/verify-email/{verification_token}"
            send_verification_email_task.delay(user.email, verification_url)

            return Response(
                {
                    "message": "Foydalanuvchi yaratildi. Iltimos emailingizni tasdiqlang.",
                    "data": serializer.data,
                },
                status=201,
            )

        except Exception as e:
            # Xatolik yuz berganda foydalanuvchini o'chiramiz
            if "user" in locals():
                user.delete()
            return Response({"message": f"Xatolik yuz berdi: {str(e)}"}, status=400)

    @action(detail=False, methods=["get"], url_path="verify-email/(?P<token>[^/.]+)")
    def verify_email(self, request, token=None):
        # Cache dan token ma'lumotlarini olish
        cache_key = f"email_verification_{token}"
        cache_data = cache.get(cache_key)

        if not cache_data:
            return Response({"message": "Noto'g'ri yoki yaroqsiz token."}, status=400)

        try:
            user = CustomUser.objects.get(id=cache_data["user_id"])

            # Vaqt tekshiruvi
            elapsed_time = timezone.now().timestamp() - cache_data["timestamp"]
            if elapsed_time > 300:  # 5 daqiqa
                cache.delete(cache_key)
                if not user.is_active:
                    user.delete()
                return Response(
                    {
                        "message": "Tasdiqlash muddati tugagan. Iltimos, qaytadan ro'yxatdan o'ting."
                    },
                    status=400,
                )

            user.is_active = True
            user.save()

            # Cache dan token ni o'chirish
            cache.delete(cache_key)

            return Response({"message": "Email muvaffaqiyatli tasdiqlandi."})

        except CustomUser.DoesNotExist:
            return Response({"message": "Foydalanuvchi topilmadi."}, status=400)

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
        logout(request)
        return Response(status=200)


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
