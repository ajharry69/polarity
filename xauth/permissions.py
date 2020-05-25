from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndOwner(BasePermission):
    """
    Allows access only to authenticated users who own the object(s)
    in question.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsSuperUser(BasePermission):
    """
    Allows access only to superuser(s).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsSuperUserOrReadOnly(BasePermission):
    """
    Allows WRITE privilege only to superuser(s) and READ to everyone else.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_superuser
        )
