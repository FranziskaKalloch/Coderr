from rest_framework.permissions import BasePermission

class IsReviewOwner(BasePermission):
    ''' Allow access only to the user who created the review. '''
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user