from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [

    # =========================
    # INICIO
    # =========================

    path(
        "",
        views.index,
        name="home",
    ),

    # =========================
    # CATEGORÍAS
    # =========================

    path(
        "categorias/",
        views.lista_categorias,
        name="categorias",
    ),

    path(
        "categorias/nueva/",
        views.nueva_categoria,
        name="nueva_categoria",
    ),

    path(
        "categorias/<int:pk>/editar/",
        views.editar_categoria,
        name="editar_categoria",
    ),

    path(
        "categorias/<int:pk>/eliminar/",
        views.eliminar_categoria,
        name="eliminar_categoria",
    ),

    # =========================
    # HERRAMIENTAS
    # =========================

    path(
        "herramientas/",
        views.herramienta_list,
        name="herramientas",
    ),

    path(
        "herramientas/nueva/",
        views.nueva_herramienta,
        name="nueva_herramienta",
    ),

    path(
        "herramientas/<int:pk>/editar/",
        views.editar_herramienta,
        name="editar_herramienta",
    ),

    path(
        "herramientas/<int:pk>/eliminar/",
        views.eliminar_herramienta,
        name="eliminar_herramienta",
    ),

    path(
        "herramientas/<int:pk>/dar-de-baja/",
        views.dar_de_baja_herramienta,
        name="dar_de_baja_herramienta",
    ),

    path(
        "herramientas/<int:pk>/qr/",
        views.qr_herramienta,
        name="qr_herramienta",
    ),

    path(
        "herramientas/<int:pk>/detalle/",
        views.detalle_herramienta,
        name="detalle_herramienta",
    ),

    # =========================
    # INSUMOS
    # =========================

    path(
        "insumos/",
        views.lista_insumos,
        name="insumos",
    ),

    path(
        "insumos/nuevo/",
        views.nuevo_insumo,
        name="nuevo_insumo",
    ),

    path(
        "insumos/<int:pk>/editar/",
        views.editar_insumo,
        name="editar_insumo",
    ),

    path(
        "insumos/<int:pk>/eliminar/",
        views.eliminar_insumo,
        name="eliminar_insumo",
    ),
]
