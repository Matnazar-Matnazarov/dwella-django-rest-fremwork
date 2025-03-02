from django.contrib import admin
from django.contrib.gis.db import models
from django.contrib.gis import admin as gis_admin
from django_json_widget.widgets import JSONEditorWidget
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(gis_admin.GISModelAdmin):
    # Asosiy ko'rsatiladigan maydonlar
    list_display = (
        "name",
        "title",
        "client",
        "address",
        "is_deleted",
        "created_at",
        "updated_at",
    )

    # Filtrlash maydonlari
    list_filter = (
        "is_deleted",
        "created_at",
        "updated_at",
        "client",
        "industry",
    )

    # Qidiruv maydonlari
    search_fields = (
        "name",
        "title",
        "description",
        "client__username",
        "client__email",
        "address",
        "guid",
    )

    # O'qish-uchun maydonlar
    readonly_fields = (
        "guid",
        "created_at",
        "updated_at",
    )

    # Maydonlarni guruhlash
    fieldsets = (
        ("Asosiy ma'lumotlar", {"fields": ("name", "title", "description")}),
        ("Mijoz ma'lumotlari", {"fields": ("client",)}),
        ("Joylashuv", {"fields": ("location", "address")}),
        ("Qo'shimcha ma'lumotlar", {"fields": ("industry",)}),
        (
            "Tizim ma'lumotlari",
            {
                "fields": ("guid", "created_at", "updated_at", "is_deleted"),
                "classes": ("collapse",),
            },
        ),
    )

    # Widget'larni sozlash
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    # Sahifadagi elementlar soni
    list_per_page = 25

    # Tez harakatlar
    actions = ["soft_delete", "restore"]

    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete.short_description = "Tanlangan e'lonlarni o'chirish"

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)

    restore.short_description = "Tanlangan e'lonlarni qayta tiklash"
