# prestamos/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from core.models import Alumno, Docente, Herramienta, Prestamo


@login_required
def index(request):
    devoluciones = (
        Prestamo.objects.filter(fecha_devolucion__isnull=False)
        .select_related("alumno", "herramienta", "docente")
        .order_by("-fecha_devolucion")
    )
    return render(request, "prestamos/index.html", {"devoluciones": devoluciones})


@login_required
def activos(request):
    prestamos_activos = (
        Prestamo.objects.filter(fecha_devolucion__isnull=True)
        .select_related("alumno", "herramienta", "docente")
        .order_by("-fecha_prestamo")
    )
    return render(request, "prestamos/activos.html", {"prestamos_activos": prestamos_activos})


@login_required
def registrar_prestamo(request):
    alumnos = Alumno.objects.filter(activo=True).order_by("apellido", "nombre")
    herramientas = Herramienta.objects.filter(activo=True, estado="DISPONIBLE").order_by("nombre")
    docentes = Docente.objects.filter(activo=True).order_by("apellido", "nombre")

    if request.method == "POST":
        try:
            alumno = get_object_or_404(Alumno, legajo=request.POST.get("alumno_qr"))
            docente_id = request.POST.get("docente")
            selected_codes = request.POST.getlist("herramientas")
            if not selected_codes:
                selected_codes = request.POST.getlist("herr_qr")
            if not selected_codes:
                messages.error(request, "Seleccioná al menos una herramienta.")
                return render(
                    request,
                    "prestamos/prestamos.html",
                    {
                        "alumnos": alumnos,
                        "herramientas": herramientas,
                        "docentes": docentes,
                    },
                )

            if not docente_id:
                messages.error(request, "Seleccioná un docente.")
                return render(
                    request,
                    "prestamos/prestamos.html",
                    {
                        "alumnos": alumnos,
                        "herramientas": herramientas,
                        "docentes": docentes,
                    },
                )

            herramientas_seleccionadas = []
            for codigo in selected_codes:
                if not codigo:
                    continue
                herramienta = get_object_or_404(Herramienta, codigo=codigo)
                if not herramienta.esta_disponible():
                    messages.error(request, f"La herramienta {herramienta.nombre} no está disponible.")
                    return render(
                        request,
                        "prestamos/prestamos.html",
                        {
                            "alumnos": alumnos,
                            "herramientas": herramientas,
                            "docentes": docentes,
                        },
                    )
                herramientas_seleccionadas.append(herramienta)

            if alumno.tiene_prestamo_vencido():
                messages.warning(request, "Atención: el alumno tiene préstamos vencidos.")

            prestamos_creados = []
            for herramienta in herramientas_seleccionadas:
                prestamo = Prestamo.objects.create(
                    alumno=alumno,
                    herramienta=herramienta,
                    docente_id=docente_id,
                    fecha_prestamo=timezone.now(),
                    observaciones=request.POST.get("observaciones", ""),
                )
                prestamos_creados.append(prestamo)
                herramienta.estado = "PRESTADA"
                herramienta.save()

            messages.success(request, f"Préstamo registrado correctamente para {len(prestamos_creados)} herramienta(s).")
            return redirect("prestamos:activos")
        except Exception as e:
            messages.error(request, f"Error al registrar préstamo: {e}")
            import traceback

            traceback.print_exc()

    return render(
        request,
        "prestamos/prestamos.html",
        {
            "alumnos": alumnos,
            "herramientas": herramientas,
            "docentes": docentes,
        },
    )

@login_required
def registrar_devolucion(request, id=None):
    prestamos_activos = (
        Prestamo.objects.filter(fecha_devolucion__isnull=True)
        .select_related("alumno", "herramienta", "docente")
        .order_by("-fecha_prestamo")
    )
    context = {
        "prestamos_activos": prestamos_activos,
        "estados_devolucion": Prestamo.ESTADOS_DEVOLUCION,
    }

    if id is not None:
        context["prestamo_seleccionado"] = id

    if request.method == "POST":
        prestamo = get_object_or_404(Prestamo, pk=request.POST.get("prestamo"))
        estado = request.POST.get("estado_devolucion")
        observaciones = request.POST.get("observaciones", "")

        if not estado:
            messages.error(request, "Seleccioná el estado de la herramienta.")
            return render(request, "prestamos/devolucion.html", context)

        prestamo.registrar_devolucion(estado, observaciones)
        messages.success(request, "Devolución registrada correctamente.")
        return redirect("prestamos:devolucion")

    return render(request, "prestamos/devolucion.html", context)
