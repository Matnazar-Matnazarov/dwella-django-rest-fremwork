from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "guid",
        "name",
        "content_object",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["content_object", "is_active", "created_at", "updated_at"]
    search_fields = ["name", "content_object__name", "content_object__title"]
    ordering = ["-created_at"]
    list_per_page = 20
    list_display_links = ["id", "guid"]
    list_editable = ["is_active"]
    readonly_fields = ["guid", "created_at", "updated_at"]
    fields = ["name", "content_object", "is_active"]
    autocomplete_fields = ["content_object"]
    list_select_related = ["content_object"]
