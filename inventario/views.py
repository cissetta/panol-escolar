
import os
import qrcode

from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.urls import reverse

from core.models import (
    Alumno,
    Categoria,
    Docente,
    Herramienta,
    Insumo,
    MovimientoInsumo,
    PrestamoInsumo,
    Prestamo,
)

from accounts.decorators import solo_panolero, solo_docente, solo_alumno
from .forms import (
    CategoriaForm,
    HerramientaForm,
    InsumoForm,
    MovimientoInsumoForm,
)


# =========================================================
# INICIO
# =========================================================

@solo_docente
def index(request):

    return render(
        request,
        "inventario/index.html"
    )


# =========================================================
# CATEGORÍAS
# =========================================================

@solo_docente
def lista_categorias(request):

    categorias = Categoria.objects.all()

    return render(
        request,
        "inventario/categorias/lista.html",
        {
            "categorias": categorias
        }
    )


@solo_panolero
def nueva_categoria(request):

    if request.method == "POST":

        form = CategoriaForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Categoría creada correctamente."
            )

            return redirect(
                "inventario:categorias"
            )

    else:

        form = CategoriaForm()

    return render(
        request,
        "inventario/categorias/form.html",
        {
            "form": form
        }
    )


@solo_panolero
def editar_categoria(request, pk):

    categoria = get_object_or_404(
        Categoria,
        pk=pk
    )

    if request.method == "POST":

        form = CategoriaForm(
            request.POST,
            instance=categoria
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Categoría actualizada correctamente."
            )

            return redirect(
                "inventario:categorias"
            )

    else:

        form = CategoriaForm(
            instance=categoria
        )

    return render(
        request,
        "inventario/categorias/form.html",
        {
            "form": form
        }
    )


@solo_panolero
def eliminar_categoria(request, pk):

    categoria = get_object_or_404(
        Categoria,
        pk=pk
    )

    categoria.delete()

    messages.success(
        request,
        "Categoría eliminada correctamente."
    )

    return redirect(
        "inventario:categorias"
    )


# =========================================================
# HERRAMIENTAS
# =========================================================

@solo_alumno
def herramienta_list(request):

    herramientas = Herramienta.objects.all()

    categorias = Categoria.objects.all()

    estados = []

    for herramienta in herramientas:

        if herramienta.estado:
            estado = herramienta.get_estado_display()

            if estado not in estados:
                estados.append(estado)

    return render(
        request,
        "inventario/herramientas/lista.html",
        {
            "herramientas": herramientas,
            "categorias": categorias,
            "estados": estados,
        },
    )

# =========================================================
# GENERAR QR
# =========================================================

def generar_qr_herramienta(herramienta, request=None):

    """
    Genera un QR único para cada herramienta.

    El QR contiene la URL de detalle de esa herramienta.
    """

    # URL relativa del detalle
    ruta = reverse(
        "inventario:detalle_herramienta",
        kwargs={
            "pk": herramienta.pk
        }
    )

    # Si tenemos request, generamos una URL completa.
    if request is not None:

        url_qr = request.build_absolute_uri(ruta)

    else:

        # Fallback para generar el QR sin request.
        base_url = getattr(
            settings,
            "QR_BASE_URL",
            "http://127.0.0.1:8000"
        )

        url_qr = f"{base_url.rstrip('/')}{ruta}"

    # Crear QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(url_qr)

    qr.make(
        fit=True
    )

    imagen = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    # Guardar imagen en memoria
    buffer = BytesIO()

    imagen.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    nombre_qr = f"qr_{herramienta.codigo}.png"

    # Eliminar QR anterior
    if herramienta.qr_code:

        try:

            ruta_anterior = herramienta.qr_code.path

            if os.path.isfile(ruta_anterior):

                os.remove(ruta_anterior)

        except Exception:
            pass

    # Guardar nuevo QR
    herramienta.qr_code.save(
        nombre_qr,
        ContentFile(buffer.getvalue()),
        save=True
    )


# =========================================================
# NUEVA HERRAMIENTA
# =========================================================

@solo_panolero
def nueva_herramienta(request):

    if request.method == "POST":

        form = HerramientaForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            herramienta = form.save(commit=False)

            # Si por alguna razón no llega el estado,
            # dejamos Disponible como estado inicial.
            if not herramienta.estado:
                herramienta.estado = "DISPONIBLE"

            herramienta.save()

            # Generar QR
            generar_qr_herramienta(
                herramienta,
                request
            )

            messages.success(
                request,
                "Herramienta creada correctamente."
            )

            return redirect(
                "inventario:herramientas"
            )

    else:

        form = HerramientaForm()

    return render(
        request,
        "inventario/herramientas/form.html",
        {
            "form": form
        }
    )

# =========================================================
# EDITAR HERRAMIENTA
# =========================================================

@solo_panolero
def editar_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    if request.method == "POST":

        form = HerramientaForm(
            request.POST,
            request.FILES,
            instance=herramienta
        )

        if form.is_valid():

            herramienta = form.save()

            # Regenerar QR
            generar_qr_herramienta(
                herramienta,
                request
            )

            messages.success(
                request,
                "Herramienta actualizada y QR regenerado correctamente."
            )

            return redirect(
                "inventario:herramientas"
            )

    else:

        form = HerramientaForm(
            instance=herramienta
        )

    return render(
        request,
        "inventario/herramientas/form.html",
        {
            "form": form,
            "herramienta": herramienta
        }
    )


# =========================================================
# ELIMINAR HERRAMIENTA
# =========================================================

@solo_panolero
def eliminar_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    archivo_qr = None

    if herramienta.qr_code:

        try:

            archivo_qr = herramienta.qr_code.path

        except Exception:
            archivo_qr = None

    herramienta.delete()

    if archivo_qr:

        try:

            if os.path.isfile(archivo_qr):

                os.remove(archivo_qr)

        except Exception:
            pass

    messages.success(
        request,
        "Herramienta eliminada correctamente."
    )

    return redirect(
        "inventario:herramientas"
    )
    
@solo_panolero
def dar_de_baja_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    if request.method == "POST":

        # Cambiar el estado a BAJA
        herramienta.estado = "BAJA"
        herramienta.save()

        messages.success(
            request,
            f"La herramienta '{herramienta.nombre}' fue dada de baja correctamente."
        )

        return redirect(
            "inventario:herramientas"
        )

    return redirect(
        "inventario:herramientas"
    )


# =========================================================
# MOSTRAR QR
# =========================================================

@solo_docente
def qr_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    # Si por algún motivo no existe QR,
    # lo generamos nuevamente.
    if not herramienta.qr_code:

        generar_qr_herramienta(
            herramienta,
            request
        )

        herramienta.refresh_from_db()

    return render(
        request,
        "inventario/herramientas/qr.html",
        {
            "herramienta": herramienta
        }
    )


# =========================================================
# DETALLE DE HERRAMIENTA
# =========================================================

@solo_docente
def detalle_herramienta(request, pk):

    """
    Esta página NO requiere login.

    Es la página que abrirá el celular
    cuando escanee el QR.
    """

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    return render(
        request,
        "inventario/herramientas/detalle.html",
        {
            "herramienta": herramienta
        }
    )


# =========================================================
# INSUMOS
# =========================================================

@solo_alumno
def lista_insumos(request):
    insumos = Insumo.objects.select_related('categoria').all()
    categorias = Categoria.objects.order_by('nombre')
    return render(request, "inventario/insumos/lista.html", {
        "insumos": insumos,
        "categorias": categorias,
    })


@solo_panolero
def nuevo_insumo(request):

    if request.method == "POST":

        form = InsumoForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Insumo creado correctamente."
            )

            return redirect(
                "inventario:insumos"
            )

    else:

        form = InsumoForm()

    return render(
        request,
        "inventario/insumos/form.html",
        {
            "form": form
        }
    )


@solo_panolero
def editar_insumo(request, pk):

    insumo = get_object_or_404(
        Insumo,
        pk=pk
    )

    if request.method == "POST":

        form = InsumoForm(
            request.POST,
            request.FILES,
            instance=insumo
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Insumo actualizado correctamente."
            )

            return redirect(
                "inventario:insumos"
            )

    else:

        form = InsumoForm(
            instance=insumo
        )

    return render(
        request,
        "inventario/insumos/form.html",
        {
            "form": form
        }
    )


@solo_panolero
def eliminar_insumo(request, pk):

    insumo = get_object_or_404(Insumo, pk=pk)

    try:
        insumo.delete()
        messages.success(request, f'Insumo "{insumo.nombre}" eliminado correctamente.')
    except ProtectedError:
        messages.error(
            request,
            f'No se puede eliminar "{insumo.nombre}" porque tiene movimientos o entregas registradas. '
            f'El historial debe conservarse. Podés desactivarlo editándolo.'
        )

    return redirect("inventario:insumos")


# =========================================================
# DETALLE DE INSUMO
# =========================================================

@solo_docente
def insumo_detalle(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    movimientos = insumo.movimientos.select_related('usuario').order_by('-fecha')
    return render(request, 'inventario/insumos/insumo_detail.html', {
        'insumo': insumo,
        'movimientos': movimientos,
    })


# =========================================================
# REGISTRAR MOVIMIENTO DE INSUMO
# =========================================================

@solo_docente
def historial_movimientos(request):
    """Historial global de movimientos de insumos con filtros."""
    qs = MovimientoInsumo.objects.select_related('insumo', 'usuario').order_by('-fecha')

    # Filtros
    insumo_id   = request.GET.get('insumo', '')
    tipo        = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if insumo_id:
        qs = qs.filter(insumo_id=insumo_id)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if fecha_desde:
        qs = qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__date__lte=fecha_hasta)

    insumos = Insumo.objects.filter(activo=True).order_by('nombre')
    tipos   = MovimientoInsumo.TIPOS

    return render(request, 'inventario/insumos/historial.html', {
        'movimientos':  qs[:200],  # máximo 200 registros
        'insumos':      insumos,
        'tipos':        tipos,
        'filtro_insumo':      insumo_id,
        'filtro_tipo':        tipo,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
        'total':        qs.count(),
    })


@solo_docente
def historial_herramientas(request):
    """Historial global de préstamos de herramientas con filtros."""
    qs = Prestamo.objects.select_related(
        'herramienta', 'alumno', 'docente'
    ).order_by('-fecha_prestamo')

    # Filtros
    herramienta_id = request.GET.get('herramienta', '')
    alumno_id      = request.GET.get('alumno', '')
    estado         = request.GET.get('estado', '')
    fecha_desde    = request.GET.get('fecha_desde', '')
    fecha_hasta    = request.GET.get('fecha_hasta', '')

    if herramienta_id:
        qs = qs.filter(herramienta_id=herramienta_id)
    if alumno_id:
        qs = qs.filter(alumno_id=alumno_id)
    if estado == 'activo':
        qs = qs.filter(fecha_devolucion__isnull=True)
    elif estado == 'devuelto':
        qs = qs.filter(fecha_devolucion__isnull=False)
    if fecha_desde:
        qs = qs.filter(fecha_prestamo__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_prestamo__date__lte=fecha_hasta)

    herramientas = Herramienta.objects.filter(activo=True).order_by('nombre')
    alumnos      = Alumno.objects.filter(activo=True).order_by('apellido', 'nombre')

    return render(request, 'inventario/herramientas/historial.html', {
        'prestamos':           qs[:200],
        'total':               qs.count(),
        'herramientas':        herramientas,
        'alumnos':             alumnos,
        'filtro_herramienta':  herramienta_id,
        'filtro_alumno':       alumno_id,
        'filtro_estado':       estado,
        'filtro_fecha_desde':  fecha_desde,
        'filtro_fecha_hasta':  fecha_hasta,
    })


@solo_panolero
def nuevo_movimiento(request, pk):
    insumo   = get_object_or_404(Insumo, pk=pk)
    alumnos  = Alumno.objects.filter(activo=True).order_by('apellido', 'nombre')
    docentes = Docente.objects.filter(activo=True).order_by('apellido', 'nombre')

    TIPOS_CHOICES = [
        ('ENTRADA', 'Entrada / Compra'),
        ('ENTREGA', 'Entrega a alumno o docente'),
        ('AJUSTE',  'Ajuste manual'),
    ]

    if request.method == 'POST':
        tipo         = request.POST.get('tipo')
        cantidad_raw = request.POST.get('cantidad', '').replace(',', '.')
        observacion  = request.POST.get('observacion', '')
        alumno_id    = request.POST.get('alumno')
        docente_id   = request.POST.get('docente')

        error = None
        try:
            cantidad = Decimal(cantidad_raw)
            if tipo == 'AJUSTE':
                if cantidad == 0:
                    raise InvalidOperation
            else:
                if cantidad <= 0:
                    raise InvalidOperation
        except (InvalidOperation, ValueError):
            if tipo == 'AJUSTE':
                error = 'Ingresá un valor distinto de cero (positivo para sumar, negativo para restar).'
            else:
                error = 'Ingresá una cantidad válida mayor a cero.'

        if not tipo:
            error = 'Seleccioná el tipo de movimiento.'

        # Para ENTREGA se requiere al menos el alumno o el docente
        if tipo == 'ENTREGA' and not alumno_id and not docente_id:
            error = 'Para una entrega seleccioná al menos el alumno o el docente destinatario.'

        if not error:
            mov = MovimientoInsumo(
                insumo=insumo,
                tipo=tipo,
                cantidad=cantidad,
                observacion=observacion,
                usuario=request.user,
            )
            mov.save()  # actualiza stock_actual automáticamente

            # Si es ENTREGA anotamos el destinatario
            if tipo == 'ENTREGA':
                alumno  = Alumno.objects.filter(pk=alumno_id).first()  if alumno_id  else None
                docente = Docente.objects.filter(pk=docente_id).first() if docente_id else None

                # PrestamoInsumo solo si hay alumno Y docente (el modelo lo requiere)
                if alumno and docente:
                    PrestamoInsumo.objects.create(
                        insumo=insumo,
                        cantidad=cantidad,
                        observacion=observacion,
                        alumno=alumno,
                        docente=docente,
                    )

                # Complementar la observación con quién recibió
                destinatario = ''
                if alumno:
                    destinatario += f'Alumno: {alumno}'
                if docente:
                    destinatario += (' · ' if destinatario else '') + f'Docente: {docente}'
                if destinatario:
                    mov.observacion = (observacion + ' | ' if observacion else '') + destinatario
                    mov.save(update_fields=['observacion'])

            messages.success(request, f'Movimiento registrado: {mov.get_tipo_display()} de {cantidad} {insumo.get_unidad_display()}.')
            return redirect('inventario:insumo_detalle', pk=insumo.pk)

        messages.error(request, error)

    return render(request, 'inventario/insumos/movimiento_form.html', {
        'insumo':   insumo,
        'tipos':    TIPOS_CHOICES,
        'alumnos':  alumnos,
        'docentes': docentes,
        'titulo':   f'Registrar movimiento — {insumo.nombre}',
    })

