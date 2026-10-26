
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user_auth_app.api.urls')),
    path('api/', include('profiles_app.api.urls')),
    
    # Generiert die OpenAPI-Schema-Datei
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    # Interaktive Dokumentation zum Ausprobieren der Endpunkte
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Dokumentation zum Lesen
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
