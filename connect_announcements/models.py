from django.db import models
from accounts.base_model import BaseModel
from announcements.models import Announcement
from images.models import Image
from django.contrib.contenttypes.fields import GenericRelation
from accounts.models import CustomUser


class ConnectAnnouncement(BaseModel):
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    master = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    images = GenericRelation(Image)
    star = models.FloatField(default=0, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["announcement"], name="connect_announcement"),
            models.Index(fields=["master"], name="connect_master"),
        ]
