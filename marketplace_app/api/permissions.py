from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    """
    Permission that allows access only to users whose profile type is 'business'.

    `has_permission` checks the authenticated user's profile and returns True
    only when `profile.type == 'business'`.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.profile.type == 'business'
        except:
            return False


class IsCustomerUser(permissions.BasePermission):
    """
    Permission that allows access only to users whose profile type is 'customer'.

    `has_permission` returns True when the authenticated user's profile has
    `type == 'customer'`.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.profile.type == 'customer'
        except:
            return False


class IsReviewOwner(permissions.BasePermission):
    """
    Object-level permission ensuring the requesting user is the review creator.

    `has_object_permission` compares the `reviewer` of the review object with
    `request.user`.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
    
class IsOrderOwner(permissions.BasePermission):
    """
    Object-level permission ensuring the requesting user is the order buyer.

    `has_object_permission` compares the `buyer` of the order object with
    `request.user`.
    """

    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user