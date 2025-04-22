from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework_api_key.permissions import HasAPIKey


class HasAPIKeyOrIsAuthenticated(BasePermission):
    """
    Allow access if the request has a valid API key or is authenticated.
    """
    def has_permission(self, request, view):
        # Check if it's a read-only request
        if request.method in SAFE_METHODS:
            return True
        
        # For Google login endpoints, no need for authentication
        if request.path.endswith('/login/') or request.path.endswith('/google-login/'):
            return True
        
        # Check for API key
        has_api_key = HasAPIKey().has_permission(request, view)
        
        # Check for authentication
        is_authenticated = IsAuthenticated().has_permission(request, view)
        
        # Allow if either condition is met
        return has_api_key or is_authenticated
