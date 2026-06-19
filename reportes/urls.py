from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('',              views.index, name='index'),
    path('configuracion/', views.index, name='configuracion'),
    path('prestamos/',    views.index, name='prestamos'),
    path('inventario/',   views.index, name='inventario'),
]
