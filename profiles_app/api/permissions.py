from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsOwner(permissions.BasePermission):
    ''' Allows access only to the owner of the profile. '''
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            return obj.user == request.user