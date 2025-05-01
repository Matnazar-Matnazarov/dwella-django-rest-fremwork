from django.contrib import admin
from .models import ConnectAnnouncement
from unfold.admin import ModelAdmin


@admin.register(ConnectAnnouncement)
class ConnectAnnouncementAdmin(ModelAdmin):
    list_display = [
        "id",
        "guid",
        "announcement",
        "master",
        "star",
        "comment",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "announcement",
        "master",
        "star",
        "is_active",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "announcement__name",
        "master__username",
        "comment",
        "star",
        "announcement__client__username",
        "announcement__client__email",
        "announcement__client__phone",
    ]
    ordering = ["-created_at"]
    list_per_page = 20
    list_display_links = ["id", "guid"]
    list_editable = ["is_active"]
    readonly_fields = ["guid", "created_at", "updated_at"]
    fields = ["announcement", "master", "star", "comment", "is_active"]
    autocomplete_fields = ["announcement", "master"]
    list_select_related = ["announcement", "master"]
