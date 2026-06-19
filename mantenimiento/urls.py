from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    path('',              views.index, name='planes'),
    path('nuevo/',        views.index, name='nuevo_plan'),
    path('<int:pk>/',     views.index, name='detalle'),
    path('hoja-de-vida/', views.index, name='hoja_vida'),
]
