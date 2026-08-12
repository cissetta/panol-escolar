import qrcode
from io import BytesIO
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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


# =========================
# INICIO
# =========================

@login_required
def index(request):
    return render(
        request,
        "inventario/index.html"
    )


# =========================
# CATEGORÍAS
# =========================

@login_required
def lista_categorias(request):

    categorias = Categoria.objects.all()

    return render(
        request,
        "inventario/categorias/lista.html",
        {"categorias": categorias},
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

            return redirect("inventario:categorias")

    else:
        form = CategoriaForm()


    return render(
        request,
        "inventario/categorias/form.html",
        {"form": form},
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
                "Categoría actualizada."
            )

            return redirect("inventario:categorias")

    else:

        form = CategoriaForm(
            instance=categoria
        )


    return render(
        request,
        "inventario/categorias/form.html",
        {"form": form},
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
        "Categoría eliminada."
    )

    return redirect(
        "inventario:categorias"
    )



# =========================
# HERRAMIENTAS
# =========================

@login_required
def herramienta_list(request):

    herramientas = Herramienta.objects.all()

    return render(
        request,
        "inventario/herramientas/lista.html",
        {"herramientas": herramientas},
    )


@login_required
def nueva_herramienta(request):

    if request.method == "POST":

        form = HerramientaForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

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
        {"form": form},
    )


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

            form.save()

            messages.success(
                request,
                "Herramienta actualizada."
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
        {"form": form},
    )


@login_required
def eliminar_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    # Guardamos el archivo QR
    archivo_qr = None

    if herramienta.qr_code:
        archivo_qr = herramienta.qr_code.path


    # Eliminamos la herramienta
    herramienta.delete()


    # Eliminamos el QR si existe
    if archivo_qr:

        import os

        if os.path.isfile(archivo_qr):
            os.remove(archivo_qr)


    messages.success(
        request,
        "Herramienta eliminada correctamente."
    )


    return redirect(
        "inventario:herramientas"
    )


# =========================
# INSUMOS
# =========================

@login_required
def lista_insumos(request):

    insumos = Insumo.objects.all()

    return render(
        request,
        "inventario/insumos/lista.html",
        {"insumos": insumos},
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
        {"form": form},
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
                "Insumo actualizado."
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
        {"form": form},
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
        "Insumo eliminado."
    )

    return redirect(
        "inventario:insumos"
    )
    
    
# =========================
# QR HERRAMIENTAS
# =========================

@login_required
def qr_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    datos = (
        f"PAÑOL ESCOLAR\n"
        f"Herramienta: {herramienta.nombre}\n"
        f"ID: {herramienta.id}\n"
        f"Codigo: {getattr(herramienta, 'codigo', '')}"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    qr.add_data(datos)
    qr.make(fit=True)

    imagen = qr.make_image()

    buffer = BytesIO()
    imagen.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )
    # =========================
# VER QR GUARDADO
# =========================

@login_required
def ver_qr_herramienta(request, pk):

    herramienta = get_object_or_404(
        Herramienta,
        pk=pk
    )

    return render(
        request,
        "inventario/herramientas/qr.html",
        {
            "herramienta": herramienta
        }
    )