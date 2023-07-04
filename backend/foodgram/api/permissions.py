from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Права для имзенения рецепта"""
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user == request.user.is_admin
        )


class ReadOnly(BasePermission):
    """Права для ингридиентов и тэгов"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
