from django.contrib import admin
from .models import Image
from unfold.admin import ModelAdmin


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = [
        "id",
        "guid",
        "name",
        "content_type",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["content_type", "is_active", "created_at", "updated_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]
    list_per_page = 20
    list_display_links = ["id", "guid"]
    list_editable = ["is_active"]
    readonly_fields = ["guid", "created_at", "updated_at"]
    fields = ["name", "content_type", "object_id", "is_active"]
