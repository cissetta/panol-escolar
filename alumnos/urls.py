from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('',               views.index, name='lista'),      # Grupo 1: lista de alumnos
    path('nuevo/',         views.index, name='nuevo'),
    path('<int:pk>/',      views.index, name='detalle'),
    path('<int:pk>/editar/', views.index, name='editar'),
    path('<int:pk>/qr/',   views.index, name='qr'),
]
