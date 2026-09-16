# prestamos/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from accounts.decorators import solo_panolero, solo_docente, solo_alumno
from core.models import Alumno, ConfiguracionSistema, Docente, Herramienta, Prestamo


@solo_docente
def index(request):
    devoluciones = (
        Prestamo.objects.filter(fecha_devolucion__isnull=False)
        .select_related("alumno", "herramienta", "docente")
        .order_by("-fecha_devolucion")
    )
    return render(request, "prestamos/index.html", {"devoluciones": devoluciones})


@solo_docente
def activos(request):
    qs = (
        Prestamo.objects.filter(fecha_devolucion__isnull=True)
        .select_related("alumno", "herramienta", "docente")
    )

    # --- filtros ---
    docente_id    = request.GET.get("docente", "").strip()
    herramienta_id = request.GET.get("herramienta", "").strip()
    alumno_q      = request.GET.get("alumno", "").strip()
    estado_filtro = request.GET.get("estado", "").strip()  # 'activo' | 'vencido'

    if docente_id:
        qs = qs.filter(docente_id=docente_id)

    if herramienta_id:
        qs = qs.filter(herramienta_id=herramienta_id)

    if alumno_q:
        qs = qs.filter(
            Q(alumno__apellido__icontains=alumno_q) |
            Q(alumno__nombre__icontains=alumno_q) |
            Q(alumno__legajo__icontains=alumno_q)
        )

    if estado_filtro in ("activo", "vencido"):
        config = ConfiguracionSistema.get()
        limite = timezone.now() - timedelta(days=config.dias_maximo_prestamo)
        if estado_filtro == "vencido":
            qs = qs.filter(fecha_prestamo__lt=limite)
        else:
            qs = qs.filter(fecha_prestamo__gte=limite)

    prestamos_activos = qs.order_by("-fecha_prestamo")

    return render(request, "prestamos/activos.html", {
        "prestamos_activos": prestamos_activos,
        "docentes":     Docente.objects.filter(activo=True).order_by("apellido", "nombre"),
        "herramientas": Herramienta.objects.filter(activo=True).order_by("nombre"),
        "f_docente":     docente_id,
        "f_herramienta": herramienta_id,
        "f_alumno":      alumno_q,
        "f_estado":      estado_filtro,
    })


@solo_panolero
def registrar_prestamo(request):
    alumnos = Alumno.objects.filter(activo=True).order_by("apellido", "nombre")
    docentes = Docente.objects.filter(activo=True).order_by("apellido", "nombre")
    herramientas = Herramienta.objects.filter(activo=True).order_by("nombre")

    if request.method == "POST":
        try:
            alumno = get_object_or_404(Alumno, legajo=request.POST.get("alumno_qr"))
            codigos = request.POST.getlist("herramientas")
            docente_id = request.POST.get("docente")
            observaciones = request.POST.get("observaciones", "")
            modulo_clase = request.POST.get("modulo_clase", "")

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
                    modulo_clase=modulo_clase,
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

@solo_alumno
def mis_prestamos(request):
    """Vista para el alumno: muestra sus préstamos activos e historial."""
    perfil = getattr(request.user, 'perfil', None)
    alumno = getattr(perfil, 'alumno', None) if perfil else None

    if alumno is None:
        # Usuario con rol ALUMNO pero sin alumno vinculado
        return render(request, 'prestamos/mis_prestamos.html', {'alumno': None})

    activos = Prestamo.objects.filter(
        alumno=alumno, fecha_devolucion__isnull=True
    ).select_related('herramienta', 'docente').order_by('-fecha_prestamo')

    historial = Prestamo.objects.filter(
        alumno=alumno, fecha_devolucion__isnull=False
    ).select_related('herramienta', 'docente').order_by('-fecha_devolucion')[:20]

    return render(request, 'prestamos/mis_prestamos.html', {
        'alumno': alumno,
        'activos': activos,
        'historial': historial,
    })


@solo_panolero
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
