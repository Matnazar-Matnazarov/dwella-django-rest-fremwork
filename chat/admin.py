from django.contrib import admin
from .models import Chat
from unfold.admin import ModelAdmin


@admin.register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = [
        "id",
        "master",
        "client",
        "connect_announcement",
        "get_message",
        "get_image",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "master",
        "client",
        "connect_announcement",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "message",
        "master__username",
        "client__username",
        "connect_announcement__title",
    ]
    autocomplete_fields = ["master", "client", "connect_announcement"]
    list_select_related = ["master", "client", "connect_announcement"]
    list_per_page = 20
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "master",
        "client",
        "connect_announcement",
        "message",
        "image",
        "created_at",
        "updated_at",
    ]

    def get_message(self, obj):
        return obj.message[:20] + "..." if len(obj.message) > 20 else obj.message

    get_message.short_description = "Message"

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    get_image.short_description = "Image"
