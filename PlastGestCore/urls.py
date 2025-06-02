# ===================================
# URLS PRINCIPALES DE PLASTGEST
# Configuración de rutas del proyecto
# ===================================

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# Vista para redireccionar la raíz
def home_redirect(request):
    """Redirige desde la raíz hacia productos"""
    return redirect('lista_productos')

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Redirección desde la raíz
    path('', home_redirect, name='home'),
    
    # URLs de la aplicación inventario (incluye auth y productos)
    path('', include('inventario.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
