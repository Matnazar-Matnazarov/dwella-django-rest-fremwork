from accounts.models import CustomUser
from accounts.base_model import BaseModel
from django.contrib.gis.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from images.models import Image
from hitcount.models import Hit


# Create your models here.
class Announcement(BaseModel):
    """Model for storing announcement information"""

    name = models.CharField(max_length=255, help_text="Name of the announcement")
    title = models.CharField(max_length=255, help_text="Title of the announcement")
    description = models.TextField(
        null=True, blank=True, help_text="Detailed description of the announcement"
    )
    client = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
        help_text="User who created the announcement",
    )
    location = models.PointField(
        srid=4326, null=True, blank=True, help_text="Geographic location coordinates"
    )
    address = models.CharField(
        max_length=255, null=True, blank=True, help_text="Physical address"
    )
    industry = models.JSONField(
        null=True, blank=True, help_text="Industry related information in JSON format"
    )
    slug = models.SlugField(
        max_length=300,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text="URL-friendly version of the title",
    )
    images = GenericRelation(Image, related_query_name="announcement")
    hit_count_generic = GenericRelation(
        Hit,
        related_query_name="hit_count_generic_relation",
        object_id_field="object_pk",
        count=True,
    )

    class Meta:
        verbose_name_plural = "Announcements"
        verbose_name = "Announcement"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"], name="announcement_name_idx"),
            models.Index(fields=["title"], name="announcement_title_idx"),
        ]

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug
        from guid, name and title
        """
        if not self.slug:
            slug_str = (
                f"{str(self.guid)[:30]}-{str(self.name)[:30]}-{str(self.title)[:30]}"
            )
            self.slug = slugify(slug_str)
        super().save(*args, **kwargs)
