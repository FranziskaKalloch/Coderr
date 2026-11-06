from rest_framework.permissions import BasePermission


class IsCustomerForOrder(BasePermission):
    ''' Allow order creation only for users with a customer profile. '''
    def has_permission(self, request, view):
        if request.method != "POST": # wenn die Methode nicht POST ist, also alles andere, dann erlaube den Zugriff sofort. 
            return True
        
        profile = getattr(request.user, 'profile', None) # enthält das Profilobjekt oder NONE
        
        if profile is None:
            return False
        
        return profile.type == "customer"        

class IsBusinessUserOfOrder(BasePermission):
    ''' Allow business users to update only their own orders. '''
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check the role after the order lookup so missing orders return HTTP 404.
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False
        
        return profile.type == "business" and obj.business_user == request.user

