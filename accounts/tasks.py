from celery import shared_task
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils import timezone
from accounts.models import CustomUser
from django.conf import settings


@shared_task
def send_verification_email_task(email, verification_url):
    """Email yuborish uchun task"""
    subject = "Email tasdiqlash"
    message = (
        f"Iltimos, hisobingizni tasdiqlash uchun quyidagi havolaga kiring: {verification_url}\n"
        f"Eslatma: Havola 5 daqiqa davomida amal qiladi."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def cleanup_expired_verification_tokens():
    """
    O'chirish:
    1. Tasdiqllanmagan (is_active=False) foydalanuvchilar
    2. 5 daqiqadan oshgan foydalanuvchilar
    """
    # Hozirgi vaqtdan 5 daqiqa oldingi vaqtni hisoblash
    expiration_threshold = timezone.now() - timezone.timedelta(minutes=5)

    # Quyidagi shartlarga mos keluvchi foydalanuvchilarni topish:
    # 1. is_active=False bo'lgan
    # 2. date_joined 5 daqiqadan oldin bo'lgan
    # 3. is_staff va is_superuser bo'lmagan
    expired_users = CustomUser.objects.filter(
        is_active=False,
        date_joined__lte=expiration_threshold,
        is_staff=False,
        is_superuser=False,
    )

    # O'chirilgan foydalanuvchilar sonini saqlash
    deleted_count = expired_users.count()

    if deleted_count > 0:
        # Cache dan verification tokenlarni o'chirish
        for user in expired_users:
            cache.delete(f"email_verification_{user.id}")

        # Foydalanuvchilarni o'chirish
        expired_users.delete()

        return f"{deleted_count} ta muddati o'tgan foydalanuvchilar o'chirildi"

    return "O'chirilishi kerak bo'lgan foydalanuvchilar topilmadi"
