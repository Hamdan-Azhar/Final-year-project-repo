from rest_framework.permissions import BasePermission

class IsSubscribed(BasePermission):
    """Check if the user has an active subscription."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.subscription
        )

class IsAdmin(BasePermission):
    """Check if the user is an admin."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.admin
        )

class IsUnsubscribed(BasePermission):
    """Check if the user doesn't have a subscription."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            not request.user.subscription
        )

class IsSubscribedOrUnsubscribed(BasePermission):
    """Check if the user doesn't have a subscription."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            not request.user.admin
        )