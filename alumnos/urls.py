from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.nuevo, name='nuevo'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    
    
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),
    path('importar-csv/', views.importar_csv, name='importar_csv'),
]