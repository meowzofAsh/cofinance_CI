# accounts/permissions.py

from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """
    Autorise uniquement les clients
    
    
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "CLIENT"
        )


class IsAgent(BasePermission):
    """
    Autorise uniquement les agent
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "AGENT"
        )


class IsAdministrator(BasePermission):
    """
    Autorise uniquement les administrateurs
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsAgentOrAdministrator(BasePermission):
    """
    Autorise les agnts et les administrateurs
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in [
                "AGENT",
                "ADMIN",
            ]
        )


class IsOwnerOrAdministrator(BasePermission):
    """
    L'utilisateur peut accéder uniquement
    à ses propres données ou êtr administrateur
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return (
            obj == request.user
            or request.user.role == "ADMIN"
        )
