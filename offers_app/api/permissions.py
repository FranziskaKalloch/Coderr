from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

from profiles_app.models import Profile

class BusinessUser(BasePermission):
    ''' Allows public read access and restricts offer creation to authenticated business users.'''
    def has_permission(self, request, view): 
        user = request.user
        
        if request.method == "GET":
            return True
        
        if not user.is_authenticated: # check if the user is authenticated 
            return False
        try:
            return user.profile.type == 'business'
        except Profile.DoesNotExist:
            return False

class IsOfferOwner(BasePermission):
    """Allow changes only to the owner of an offer."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user