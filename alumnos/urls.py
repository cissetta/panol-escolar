from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('',               views.index, name='herramientas'),
    path('nueva/',         views.index, name='nueva_herramienta'),
    path('<int:pk>/',      views.index, name='detalle'),
    path('insumos/',       views.index, name='insumos'),
    path('insumos/nuevo/', views.index, name='nuevo_insumo'),
]
