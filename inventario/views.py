
import os
import qrcode

from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from core.models import (
    Categoria,
    Herramienta,
    Insumo,
    MovimientoInsumo,
)

from .forms import (
    CategoriaForm,
    HerramientaForm,
    InsumoForm,
    MovimientoInsumoForm,
)


# =========================================================
# INICIO
# =========================================================

@login_required
def index(request):

    return render(
        request,
        "inventario/index.html"
    )


# =========================================================
# CATEGORÍAS
# =========================================================

@login_required
def lista_categorias(request):

    categorias = Categoria.objects.all()

    return render(
        request,
        "inventario/categorias/lista.html",
        {
            "categorias": categorias
        }
    )


@login_required
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


@login_required
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


@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
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
    
@login_required
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

@login_required
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

@login_required
def lista_insumos(request):

    insumos = Insumo.objects.all()

    return render(
        request,
        "inventario/insumos/lista.html",
        {
            "insumos": insumos
        }
    )


@login_required
def nuevo_insumo(request):

    if request.method == "POST":

        form = InsumoForm(
            request.POST
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


@login_required
def editar_insumo(request, pk):

    insumo = get_object_or_404(
        Insumo,
        pk=pk
    )

    if request.method == "POST":

        form = InsumoForm(
            request.POST,
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


@login_required
def eliminar_insumo(request, pk):

    insumo = get_object_or_404(
        Insumo,
        pk=pk
    )

    insumo.delete()

    messages.success(
        request,
        "Insumo eliminado correctamente."
    )

    return redirect(
        "inventario:insumos"
    )

