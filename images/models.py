from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.base_model import BaseModel

# FileValidate
from django.core.validators import FileExtensionValidator


class ImageManager(models.Manager):
    def get_for_object(self, obj):
        """Get all images associated with the given object"""
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, object_id=obj.id, is_active=True)


class Image(BaseModel):
    name = models.ImageField(
        upload_to="images/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "gif", "ico", "webp"]
            )
        ],
    )
    # Add fields for generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = ImageManager()

    class Meta:
        verbose_name_plural = "Images"
        verbose_name = "Image"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.name.name
