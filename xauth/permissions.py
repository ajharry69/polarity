from rest_framework.permissions import BasePermission


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
