from django.contrib.gis import forms as gis_forms
from django_json_widget.widgets import JSONEditorWidget
from unfold.admin import ModelAdmin
from django import forms
from .models import Announcement
from django.contrib import admin
from django.utils.html import format_html
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminTextareaWidget
from hitcount.models import Hit, HitCount
from django.contrib.contenttypes.models import ContentType


class AnnouncementAdminForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = "__all__"
        widgets = {
            "location": gis_forms.OSMWidget(attrs={'default_zoom': 12}),
            "industry": JSONEditorWidget(attrs={'style': 'height: 300px'}),
            "name": UnfoldAdminTextInputWidget(),
            "title": UnfoldAdminTextInputWidget(),
            "description": UnfoldAdminTextareaWidget(attrs={'rows': 5}),
            "address": UnfoldAdminTextInputWidget(),
        }

@admin.register(Announcement)
class AnnouncementAdmin(ModelAdmin):
    form = AnnouncementAdminForm
    
    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/ol@v7.3.0/ol.css",
                "/static/css/custom_map.css",
            ),
        }
        js = (
            "https://cdn.jsdelivr.net/npm/ol@v7.3.0/dist/ol.js",
        )

    list_display = (
        "name",
        "title",
        "client_info",
        "address",
        "status_badge",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_deleted",
        "is_active",
        "created_at",
        "updated_at",
        "client__role",
    )

    search_fields = (
        "name",
        "title",
        "description",
        "client__username",
        "client__email",
        "address",
        "guid",
    )

    readonly_fields = (
        "guid",
        "created_at",
        "updated_at",
        "hit_count",
    )

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": (
                "name",
                "title",
                "description",
            ),
            "description": "E'lonning asosiy ma'lumotlari",
        }),
        ("Mijoz ma'lumotlari", {
            "fields": (
                "client",
            ),
            "description": "E'lon egasi haqida ma'lumot",
        }),
        ("Joylashuv", {
            "fields": (
                "location",
                "address",
            ),
            "description": "E'lonning joylashuvi va manzili",
        }),
        ("Qo'shimcha ma'lumotlar", {
            "fields": (
                "industry",
                "hit_count",
            ),
            "description": "E'lon haqida qo'shimcha ma'lumotlar",
        }),
        ("Tizim ma'lumotlari", {
            "fields": (
                "guid",
                "created_at",
                "updated_at",
                "is_deleted",
                "is_active",
            ),
            "classes": ("collapse",),
            "description": "Tizim tomonidan boshqariladigan ma'lumotlar",
        }),
    )

    list_per_page = 25
    save_on_top = True
    show_full_result_count = True
    preserve_filters = True

    actions = ["soft_delete", "restore", "make_active", "make_inactive"]

    def status_badge(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">●</span> O\'chirilgan')
        elif not obj.is_active:
            return format_html('<span style="color: orange;">●</span> Faol emas')
        return format_html('<span style="color: green;">●</span> Faol')
    status_badge.short_description = "Holati"

    def client_info(self, obj):
        if obj.client:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" width="30" height="30" style="border-radius: 50%; margin-right: 10px;" />'
                '<div>'
                '<div>{}</div>'
                '<div style="color: gray; font-size: 0.8em;">{}</div>'
                '</div>'
                '</div>',
                obj.client.picture.url if obj.client.picture else '/static/users/default-avatar.png',
                obj.client.get_full_name or obj.client.username,
                obj.client.email
            )
        return "-"
    client_info.short_description = "Mijoz"

    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = "Tanlangan e'lonlarni o'chirish"

    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = "Tanlangan e'lonlarni qayta tiklash"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Tanlangan e'lonlarni faollashtirish"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Tanlangan e'lonlarni faolsizlantirish"

    def hit_count(self, obj):
        ctype = ContentType.objects.get_for_model(Announcement)
        try:
            hitcount = HitCount.objects.get(content_type=ctype, object_pk=str(obj.pk))
            return hitcount.hits
        except HitCount.DoesNotExist:
            return 0
    hit_count.short_description = "Ko'rishlar soni"