import os
from celery import Celery

# Django settings modulini ko'rsatish
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Celery ilovasini yaratish
app = Celery("config")

# Django settings faylidan konfiguratsiyani o'qish
app.config_from_object("django.conf:settings", namespace="CELERY")

# Task larni avtomatik yuklash
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    "cleanup-expired-tokens": {
        "task": "accounts.tasks.cleanup_expired_verification_tokens",
        "schedule": 300.0,  # Har 5 daqiqada (300 sekund)
    },
}
