from rest_framework import permissions

class IsOwnProfile(permissions.BasePermission):
    """
    Custom permission: Users can only edit their own profile
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True
  
        return obj.user == request.user