from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.urls import path
from django.utils.html import format_html
from .forms import AdminLoginForm
from .models import CustomUser, Like


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin configuration for CustomUser model"""

    list_display = (
        "username",
        "email",
        "full_name",
        "role",
        "status_badge",
        "last_login",
    )
    list_display_links = ("username", "email")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    list_filter = ("is_active", "is_staff", "is_superuser", "role", "date_joined")
    ordering = ("username",)
    list_per_page = 25
    date_hierarchy = "date_joined"

    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "picture",
                )
            },
        ),
        ("Role & Status", {"fields": ("role", "is_online", "end_of_session")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("date_joined", "last_login")

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')

    status_badge.short_description = "Status"

    def full_name(self, obj):
        return obj.get_full_name

    full_name.short_description = "Full Name"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin configuration for Like model"""

    list_display = ("user", "master", "is_like", "created_at")
    list_display_links = ("user", "master")
    search_fields = ("user__username", "master__username")
    list_filter = ("is_like", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("user", "master")

    # def has_add_permission(self, request):
    #     return False


# class CustomAdminSite(AdminSite):
#     """Custom admin site configuration"""
#     site_header = 'Dwella Administration'
#     site_title = 'Dwella Admin Portal'
#     index_title = 'Welcome to Dwella Admin Portal'
#     login_form = AdminLoginForm

#     def get_app_list(self, request):
#         app_list = super().get_app_list(request)
#         # Customize the order of apps
#         app_ordering = {
#             'accounts': 1,
#             'auth': 2,
#             'captcha': 3,  # CAPTCHA-ni app listga qo'shamiz
#         }
#         app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 10))
#         return app_list

#     def login(self, request, extra_context=None):
#         """Add CAPTCHA to login page"""
#         if request.method == 'POST':
#             form = self.login_form(request.POST)
#             if form.is_valid():
#                 return super().login(request)
#         else:
#             form = self.login_form()

#         context = {
#             **self.each_context(request),
#             'title': 'Log in',
#             'form': form,
#             **(extra_context or {}),
#         }
#         return super().login(request, extra_context=context)

# admin_site = CustomAdminSite(name='custom_admin')

# admin.site.site_header = 'Dwella Administration'
# admin.site.site_title = 'Dwella Admin Portal'
# admin.site.index_title = 'Welcome to Dwella Admin Portal'
