from django.urls import path

from . import views

app_name = "prestamos"

urlpatterns = [

    path(
        "",
        views.index,
        name="lista"
    ),

    path(
        "nuevo/",
        views.registrar_prestamo,
        name="nuevo"
    ),

    path(
        "activos/",
        views.activos,
        name="activos"
    ),

    path(
        "devolucion/",
        views.registrar_devolucion,
        name="devolucion"
    ),

    path(
        "devolver/<int:id>/",
        views.registrar_devolucion,
        name="devolver"
    ),

    path(
        "devolucion/<int:id>/",
        views.registrar_devolucion,
        name="devolucion_seleccionada"
    ),
]
