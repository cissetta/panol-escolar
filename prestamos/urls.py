from django.urls import path
from . import views

app_name = 'prestamos'

urlpatterns = [
    path('',           views.index, name='lista'),
    path('nuevo/',     views.index, name='nuevo'),
    path('devolucion/', views.index, name='devolucion'),
    path('<int:pk>/',  views.index, name='detalle'),
]
