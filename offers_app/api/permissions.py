from rest_framework.permissions import BasePermission, IsAuthenticated

from profiles_app import Profile

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
        