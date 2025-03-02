from django.db import models
from accounts.base_model import BaseModel
from accounts.models import CustomUser
from connect_announcements.models import ConnectAnnouncement
from django.core.validators import FileExtensionValidator


class Chat(BaseModel):
    message = models.TextField(null=True, blank=True)
    connect_announcement = models.ForeignKey(
        ConnectAnnouncement, on_delete=models.SET_NULL, null=True, blank=True
    )
    master = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="master_chats",
    )
    client = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_chats",
    )
    image = models.ImageField(
        upload_to="chat/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )

    class Meta:
        indexes = [
            models.Index(fields=["master"], name="master_index_chat"),
            models.Index(fields=["client"], name="client_index_chat"),
        ]
