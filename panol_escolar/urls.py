"""
urls.py – Enrutamiento principal del proyecto
PROA Villa del Totoral – Programación IV 2026
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',         admin.site.urls),
    path('accounts/',      include('accounts.urls')),
    path('',               include('core.urls')),
    path('alumnos/',       include('alumnos.urls')),
    path('inventario/',    include('inventario.urls')),
    path('prestamos/',     include('prestamos.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
    path('reportes/',      include('reportes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
