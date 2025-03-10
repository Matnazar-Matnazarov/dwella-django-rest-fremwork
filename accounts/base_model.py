from django.db import models
import uuid


class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class BaseModel(models.Model):
    guid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    objects = BaseManager()
    deleted_objects = DeletedManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["guid"], name="guid_index"),
            models.Index(fields=["created_at"], name="created_at_index"),
            models.Index(fields=["is_deleted"], name="is_deleted_index"),
            models.Index(fields=["is_active"], name="is_active_index"),
        ]

    def soft_delete(self):
        """Obyektni yumshoq o'chirish"""
        self.is_deleted = True
        self.save()

    def restore(self):
        """O'chirilgan obyektni qayta tiklash"""
        self.is_deleted = False
        self.save()

    def __str__(self):
        """Obyekt string ko'rinishi"""
        return f"{self.__class__.__name__}({self.guid})"

    