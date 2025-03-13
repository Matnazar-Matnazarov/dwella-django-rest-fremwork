from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import HasAPIKey


class HasAPIKeyOrIsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # API key headerini tekshirish
        api_key = request.META.get("HTTP_X_API_KEY", "")

        # JWT token tekshirish
        is_authenticated = bool(request.user and request.user.is_authenticated)

        if not api_key or not is_authenticated:
            return False

        # API key validatsiyasi
        try:
            from rest_framework_api_key.models import APIKey

            api_key_object = APIKey.objects.get_from_key(api_key)
            if not api_key_object.is_valid(api_key):
                return False

            # API key valid va JWT token ham valid bo'lsa
            return True

        except Exception:
            return False
