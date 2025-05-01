from django.contrib import admin
from unfold.admin import ModelAdmin
from django_celery_beat.models import (
    SolarSchedule,
    IntervalSchedule,
    ClockedSchedule,
    CrontabSchedule,
    PeriodicTasks,
    PeriodicTask,
)
from rest_framework.authtoken.models import Token
from django.utils.html import format_html
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.sites.models import Site
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.admin import APIKeyModelAdmin


admin.site.unregister(APIKey)
@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin, APIKeyModelAdmin):
    list_display = ("name", "prefix", "created", "revoked")
    readonly_fields = ("prefix", "created", "revoked")
    search_fields = ("name", "prefix")
    ordering = ("-created",)


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    list_display = ("key", "user", "created")
    list_filter = ("created",)
    search_fields = ("key", "user__username", "user__email")
    readonly_fields = ("key", "created")
    ordering = ("-created",)

    fieldsets = (
        ("Token Information", {
            "fields": ("key", "user")
        }),
        ("Dates", {
            "fields": ("created",),
            "classes": ("collapse",)
        }),
    )


# Unregister default admin classes
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)


@admin.register(SocialAccount)
class SocialAccountAdmin(ModelAdmin):
    list_display = ('user', 'provider', 'uid', 'last_login', 'date_joined')
    list_filter = ('provider', 'last_login', 'date_joined')
    search_fields = ('user__username', 'user__email', 'uid', 'extra_data')
    raw_id_fields = ('user',)
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'provider', 'uid')
        }),
        ('Additional Data', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialApp)
class SocialAppAdmin(ModelAdmin):
    list_display = ('name', 'provider', 'client_id')
    list_filter = ('provider',)
    search_fields = ('name', 'client_id')
    filter_horizontal = ('sites',)

    fieldsets = (
        ('App Information', {
            'fields': ('name', 'provider', 'client_id', 'secret', 'key')
        }),
        ('Sites', {
            'fields': ('sites',),
            'description': 'Select the sites where this social app will be available.'
        }),
    )


@admin.register(SocialToken)
class SocialTokenAdmin(ModelAdmin):
    list_display = ('app', 'account', 'truncated_token', 'expires_at')
    list_filter = ('app__provider', 'expires_at')
    raw_id_fields = ('app', 'account')
    search_fields = ('token', 'account__user__username', 'app__name')
    
    def truncated_token(self, obj):
        if obj.token:
            return f"{obj.token[:10]}..."
        return "-"
    truncated_token.short_description = "Token"

    fieldsets = (
        ('Token Information', {
            'fields': ('app', 'account', 'token', 'token_secret')
        }),
        ('Expiration', {
            'fields': ('expires_at',),
            'classes': ('collapse',)
        }),
    )


admin.site.unregister(IntervalSchedule)
@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    list_display = ("every", "period")
    list_filter = ("period",)
    search_fields = ("every", "period")
    ordering = ("every",)

    fieldsets = (
        ("Schedule Information", {
            "fields": ("every", "period")
        }),
    )


admin.site.unregister(CrontabSchedule)
@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(ModelAdmin):
    list_display = ("minute", "hour", "day_of_week", "day_of_month", "month_of_year")
    list_filter = ("day_of_week", "month_of_year")
    search_fields = ("minute", "hour", "day_of_week", "day_of_month", "month_of_year")
    ordering = ("minute", "hour")

    fieldsets = (
        ("Schedule Information", {
            "fields": (
                ("minute", "hour"),
                ("day_of_week", "day_of_month"),
                "month_of_year",
            )
        }),
    )


admin.site.unregister(SolarSchedule)
@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    list_display = ("event", "latitude", "longitude")
    list_filter = ("event",)
    search_fields = ("event", "latitude", "longitude")
    ordering = ("event",)

    fieldsets = (
        ("Schedule Information", {
            "fields": (
                "event",
                ("latitude", "longitude"),
            )
        }),
    )


admin.site.unregister(ClockedSchedule)
@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(ModelAdmin):
    list_display = ("clocked_time",)
    search_fields = ("clocked_time",)
    ordering = ("clocked_time",)

    fieldsets = (
        ("Schedule Information", {
            "fields": ("clocked_time",)
        }),
    )


admin.site.unregister(PeriodicTask)
@admin.register(PeriodicTask)
class PeriodicTaskAdmin(ModelAdmin):
    list_display = ("name", "task", "enabled", "last_run_at", "total_run_count", "schedule_display")
    list_filter = ("enabled", "last_run_at")
    search_fields = ("name", "task", "args", "kwargs")
    ordering = ("name",)
    readonly_fields = ("last_run_at", "total_run_count", "schedule_display")
    list_per_page = 25

    fieldsets = (
        ("Task Information", {
            "fields": (
                "name",
                "task",
                "enabled",
            )
        }),
        ("Schedule", {
            "fields": (
                "interval",
                "crontab",
                "solar",
                "clocked",
                "one_off",
            )
        }),
        ("Task Arguments", {
            "fields": (
                "args",
                "kwargs",
            ),
            "classes": ("collapse",)
        }),
        ("Statistics", {
            "fields": (
                "last_run_at",
                "total_run_count",
            ),
            "classes": ("collapse",)
        }),
    )

    def schedule_display(self, obj):
        if obj.interval:
            return format_html(
                '<span style="color: #28a745;">Interval: {}</span>',
                f"{obj.interval.every} {obj.interval.period}"
            )
        elif obj.crontab:
            return format_html(
                '<span style="color: #17a2b8;">Crontab: {}</span>',
                f"{obj.crontab.minute} {obj.crontab.hour} {obj.crontab.day_of_week} {obj.crontab.day_of_month} {obj.crontab.month_of_year}"
            )
        elif obj.solar:
            return format_html(
                '<span style="color: #ffc107;">Solar: {}</span>',
                obj.solar.event
            )
        elif obj.clocked:
            return format_html(
                '<span style="color: #dc3545;">Clocked: {}</span>',
                obj.clocked.clocked_time
            )
        return format_html('<span style="color: #6c757d;">No schedule</span>')

    schedule_display.short_description = "Schedule"


@admin.register(PeriodicTasks)
class PeriodicTasksAdmin(ModelAdmin):
    list_display = ("ident", "last_update")
    readonly_fields = ("ident", "last_update")
    ordering = ("-last_update",)

    fieldsets = (
        ("Task Information", {
            "fields": ("ident",)
        }),
        ("Timestamps", {
            "fields": ("last_update",),
            "classes": ("collapse",)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


