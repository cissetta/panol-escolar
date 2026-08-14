from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('',              views.index, name='index'),
    path('docentes/',              views.docentes, name='docentes'),
    path('docentes/<int:pk>/editar/', views.editar_docente, name='editar_docente'),
    path('docentes/<int:pk>/eliminar/', views.eliminar_docente, name='eliminar_docente'),
    path('categorias/',              views.categorias, name='categorias'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/exportar-excel/', views.exportar_reportes_excel, name='exportar_reportes_excel'),
    path('prestamos/',    views.index, name='prestamos'),
    path('inventario/',   views.index, name='inventario'),
]