"""
urls.py – Enrutamiento principal del proyecto
PROA Villa del Totoral – Programación IV 2026

Cada grupo incluye las URLs de su app aquí al terminar su módulo.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración Django
    path('admin/', admin.site.urls),

    # Autenticación (Tech Lead – ya implementado)
    path('accounts/', include('accounts.urls')),

    # Dashboard y páginas base (Tech Lead – ya implementado)
    path('', include('core.urls')),

    # ── Apps de los grupos ──────────────────────────────────────
    # Descomentar a medida que cada grupo entregue su módulo
    path('alumnos/',       include('alumnos.urls')),        # Grupo 1
    path('inventario/',    include('inventario.urls')),     # Grupo 2
    path('prestamos/',     include('prestamos.urls')),      # Grupo 3
    path('mantenimiento/', include('mantenimiento.urls')),  # Grupo 4
    path('reportes/',      include('reportes.urls')),       # Grupo 5

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
