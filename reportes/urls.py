from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('',              views.index, name='index'),
    path('docentes/',              views.docentes, name='docentes'),
    path('categorias/',              views.categorias, name='categorias'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('prestamos/',    views.index, name='prestamos'),
    path('inventario/',   views.index, name='inventario'),
]