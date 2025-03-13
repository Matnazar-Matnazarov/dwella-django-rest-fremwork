from django.contrib import admin
from django.utils.html import format_html
from .models import Industry, IndustryUser


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(IndustryUser)
class IndustryUserAdmin(admin.ModelAdmin):
    list_display = ("get_industry", "price", "star", "get_status")
    list_filter = ("industry", "star", "created_at")
    search_fields = ("user__username", "user__email", "industry__name")
    autocomplete_fields = ["user", "industry"]
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        ("User Information", {"fields": ("user", "industry")}),
        ("Service Details", {"fields": ("price", "internship", "star")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_industry(self, obj):
        if obj.industry:
            return obj.industry.name
        return "-"

    get_industry.short_description = "Industry"
    get_industry.admin_order_field = "industry__name"

    def get_status(self, obj):
        if obj.star is None:
            return "-"
        if obj.star >= 4:
            return format_html('<span style="color: green;">★ {}</span>', obj.star)
        elif obj.star >= 2:
            return format_html('<span style="color: orange;">★ {}</span>', obj.star)
        else:
            return format_html('<span style="color: red;">★ {}</span>', obj.star)

    get_status.short_description = "Rating"
    get_status.admin_order_field = "star"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "industry")
