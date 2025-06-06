from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAdminOrDisallowDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "DELETE" and not request.user.is_staff:
            raise PermissionDenied("You cannot delete the user directly")

        return True
