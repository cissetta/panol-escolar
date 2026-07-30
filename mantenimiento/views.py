from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from core.models import (
    Herramienta,
    PlanMantenimiento,
    EjecucionMantenimiento,
    TareaMantenimiento,
    LogHerramienta,
)


def index(request):
    herramienta_id = request.GET.get("herramienta")
    mes = request.GET.get("mes")

    herramientas = Herramienta.objects.filter(activo=True)

    planes = PlanMantenimiento.objects.select_related(
        "herramienta"
    ).all()

    historial = EjecucionMantenimiento.objects.select_related(
        "plan",
        "plan__herramienta"
    ).all()

    if herramienta_id:
        planes = planes.filter(herramienta_id=herramienta_id)
        historial = historial.filter(plan__herramienta_id=herramienta_id)

    if mes:
        planes = planes.filter(proxima_ejecucion__month=int(mes))
        historial = historial.filter(fecha__month=int(mes))

    historial = historial.order_by("-fecha")

    return render(
        request,
        "mantenimiento/index.html",
        {
            "planes": planes,
            "historial": historial,
            "herramientas": herramientas,
            "herramienta_seleccionada": herramienta_id,
            "mes_seleccionado": mes,
        }
    )

    return render(
        request,
        "mantenimiento/index.html",
        {
            "planes": planes,
            "historial": historial,
            "herramientas": herramientas,
            "herramienta_seleccionada": herramienta_id,
            "mes_seleccionado": mes,
        }
    )
    return render(
        request,
        "mantenimiento/index.html",
        {
            "planes": planes,
            "historial": historial,
            "herramientas": herramientas,
            "herramienta_seleccionada": herramienta_id,
        }
    )

def crear_plan(request):

    herramientas = Herramienta.objects.filter(activo=True)

    if request.method == "POST":

        try:

            herramienta = Herramienta.objects.get(
                id=request.POST.get("herramienta")
            )

            frecuencia = request.POST.get("frecuencia_dias")

            # Crear el plan
            plan = PlanMantenimiento.objects.create(
                nombre=request.POST.get("nombre"),
                herramienta=herramienta,
                tipo=request.POST.get("tipo"),
                descripcion=request.POST.get("descripcion"),
                frecuencia_dias=frecuencia if frecuencia else None,
                proxima_ejecucion=request.POST.get("proxima_ejecucion"),
                activo=True,
            )

            # Crear las tareas
            descripciones = request.POST.getlist("descripcion_tarea[]")
            responsables = request.POST.getlist("responsable_tarea[]")
            duraciones = request.POST.getlist("duracion_tarea[]")

            for i in range(len(descripciones)):

                if descripciones[i].strip():

                    TareaMantenimiento.objects.create(
                        plan=plan,
                        descripcion=descripciones[i],
                        responsable=responsables[i],
                        duracion_estimada_min=duraciones[i] or None,
                        orden=i + 1,
                    )

            messages.success(
                request,
                "✅ Plan y tareas creados correctamente."
            )

            return redirect("mantenimiento:index")

        except Exception as e:

            messages.error(
                request,
                f"Error: {e}"
            )

    return render(
        request,
        "mantenimiento/crear_plan.html",
        {
            "herramientas": herramientas,
        },
    )

def ejecutar_plan(request, plan_id):

    plan = get_object_or_404(
        PlanMantenimiento,
        pk=plan_id
    )

    tareas = plan.tareas.all()

    if request.method == "POST":

        ejecucion = EjecucionMantenimiento.objects.create(

            plan=plan,

            realizado_por=request.POST.get(
                "realizado_por"
            ),

            es_externo=request.POST.get(
                "es_externo"
            ) == "on",

            costo=request.POST.get(
                "costo"
            ) or 0,

            notas=request.POST.get(
                "notas"
            ),
        )

        tareas_ids = request.POST.getlist(
            "tareas_completadas"
        )

        if tareas_ids:
            tareas_completadas = tareas.filter(
                id__in=tareas_ids
            )

            ejecucion.tareas_completadas.set(
                tareas_completadas
            )

        messages.success(
            request,
            "✅ Mantenimiento registrado correctamente."
        )

        return redirect("mantenimiento:index")

    return render(
        request,
        "mantenimiento/ejecutar_plan.html",
        {
            "plan": plan,
            "tareas": tareas,
        }
    )


def plan_de_vida(request, herramienta_id):

    herramienta = get_object_or_404(
        Herramienta,
        pk=herramienta_id
    )

    planes = PlanMantenimiento.objects.filter(
        herramienta=herramienta
    )

    historial = EjecucionMantenimiento.objects.filter(
        plan__herramienta=herramienta
    ).order_by("-fecha")

    return render(
        request,
        "mantenimiento/plan_de_vida.html",
        {
            "herramienta": herramienta,
            "planes": planes,
            "historial": historial,
        }
    )

def detalle_plan(request, plan_id):

    plan = get_object_or_404(
        PlanMantenimiento.objects.select_related(
            "herramienta"
        ),
        pk=plan_id
    )

    tareas = plan.tareas.all()

    ejecuciones = plan.ejecuciones.all().order_by(
        "-fecha"
    )

    return render(
        request,
        "mantenimiento/detalle_plan.html",
        {
            "plan": plan,
            "tareas": tareas,
            "ejecuciones": ejecuciones,
        }
    )