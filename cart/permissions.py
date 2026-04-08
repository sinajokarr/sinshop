from rest_framework import permissions

class IsCartOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user is None:
            return True
        return obj.user == request.user