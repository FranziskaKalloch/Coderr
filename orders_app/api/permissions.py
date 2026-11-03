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
        profile = getattr(request.user, "profile", None)
        if profile is None:
            return False
        
        return request.user.is_authenticated and profile.type == "business"
    
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user

