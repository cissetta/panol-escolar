from django.urls import path
from . import views

app_name = "mantenimiento"

urlpatterns = [

    path(
        "",
        views.index,
        name="index",
    ),

    path(
        "crear-plan/",
        views.crear_plan,
        name="crear_plan",
    ),

    path(
        "ejecutar/<int:plan_id>/",
        views.ejecutar_plan,
        name="ejecutar_plan",
    ),

    path(
        "detalle/<int:plan_id>/",
        views.detalle_plan,
        name="detalle_plan",
    ),

    path(
        "plan_de_vida/<int:herramienta_id>/",
        views.plan_de_vida,
        name="plan_de_vida",
    ),
    path(
        "editar/<int:plan_id>/",
        views.editar_plan,
        name="editar_plan",
    ),

    path(
        "eliminar/<int:plan_id>/",
        views.eliminar_plan,
        name="eliminar_plan",
    ),
]