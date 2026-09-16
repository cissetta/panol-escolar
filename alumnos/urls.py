from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('',                   views.lista,              name='lista'),
    path('nuevo/',             views.nuevo,              name='nuevo'),
    path('exportar-csv/',      views.exportar_csv,       name='exportar_csv'),
    path('importar-csv/',      views.importar_csv,       name='importar_csv'),
    path('generar-qr-masivo/', views.generar_qr_masivo,  name='generar_qr_masivo'),
    path('descargar-qr-zip/',  views.descargar_qr_zip,   name='descargar_qr_zip'),
    path('<int:pk>/',          views.detalle,            name='detalle'),
    path('<int:pk>/editar/',   views.editar,             name='editar'),
    path('<int:pk>/eliminar/',             views.confirmar_eliminar,    name='eliminar'),
    path('<int:pk>/reactivar/',            views.reactivar,             name='reactivar'),
    path('<int:pk>/eliminar-definitivo/',  views.eliminar_definitivo,   name='eliminar_definitivo'),
]
