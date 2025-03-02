from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .base_model import BaseModel
import re


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "CLIENT", "Client"
    MASTER = "MASTER", "Master"
    MANAGER = "MANAGER", "Manager"


class CustomUserManager(UserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", Role.USER)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)
        return self._create_user(username, email, password, **extra_fields)


class PhoneNumberValidator(object):
    def __init__(self, regex=r"^\+?1?\d{9,15}$", message=None):
        self.regex = regex
        self.message = message or "Enter a valid phone number."

    def __call__(self, value):
        if not re.match(self.regex, value):
            raise ValidationError(self.message, code="invalid")
    
    def deconstruct(self):
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}",
            [],
            {
                "regex": self.regex,
                "message": self.message,
            },
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[PhoneNumberValidator()],
        db_index=True,
        unique=True,
    )
    picture = models.ImageField(
        upload_to="users/",
        null=True,
        blank=True,
        default="users/default-avatar.png",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )
    role = models.CharField(
        max_length=255, null=True, blank=True, choices=Role.choices, default=Role.USER
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    end_of_session = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_short_name(self):
        return self.first_name

    @property
    def count_likes(self):
        return Like.objects.filter(master=self, is_like=True).count()

    @property
    def count_dislikes(self):
        return Like.objects.filter(master=self, is_like=False).count()


class Like(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="likes_given",
        null=True,
        blank=True,
    )
    master = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="likes_received",
        null=True,
        blank=True,
    )
    is_like = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"], name="user_index"),
            models.Index(fields=["master"], name="master_index"),
        ]
