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
    herramientas = Herramienta.objects.filter(activo=True).order_by("nombre")
    docentes = Docente.objects.filter(activo=True).order_by("apellido", "nombre")

    if request.method == "POST":
        try:
            alumno = get_object_or_404(Alumno, legajo=request.POST.get("alumno_qr"))
            codigos = request.POST.getlist("herramientas")
            docente_id = request.POST.get("docente")
            observaciones = request.POST.get("observaciones", "")

            ctx = {"alumnos": alumnos, "herramientas": herramientas, "docentes": docentes}

            if not docente_id:
                messages.error(request, "Seleccioná un docente.")
                return render(request, "prestamos/prestamos.html", ctx)

            if not codigos:
                messages.error(request, "Seleccioná al menos una herramienta.")
                return render(request, "prestamos/prestamos.html", ctx)

            if alumno.tiene_prestamo_vencido():
                messages.warning(request, "Atención: el alumno tiene préstamos vencidos.")

            registradas = []
            no_disponibles = []
            for codigo in codigos:
                herr = Herramienta.objects.filter(codigo=codigo).first()
                if herr is None:
                    continue
                if not herr.esta_disponible():
                    no_disponibles.append(herr.nombre)
                    continue
                Prestamo.objects.create(
                    alumno=alumno,
                    herramienta=herr,
                    docente_id=docente_id,
                    fecha_prestamo=timezone.now(),
                    observaciones=observaciones,
                )
                herr.estado = "PRESTADA"
                herr.save()
                registradas.append(herr.nombre)

            if registradas:
                messages.success(request, f"Préstamo registrado: {', '.join(registradas)}.")
            if no_disponibles:
                messages.warning(request, f"No disponibles (omitidas): {', '.join(no_disponibles)}.")

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
