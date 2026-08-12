# Grupo 5 – Reportes y Dashboard
# TODO: implementar las vistas de este módulo
import json
from datetime import datetime
from django import forms
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.utils import timezone
from core.models import Herramienta, Insumo, Prestamo, PlanMantenimiento, ConfiguracionSistema, Categoria, Docente


class ConfiguracionSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSistema
        fields = ['nombre_institucion', 'dias_maximo_prestamo', 'dias_aviso_mantenimiento', 'email_alertas']
        widgets = {
            'nombre_institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'dias_maximo_prestamo': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'dias_aviso_mantenimiento': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'email_alertas': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'color_hex']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Herramientas eléctricas'}),
            'color_hex': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }


class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = ['nombre', 'apellido', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


def _get_reportes_context():
    # Indicadores de inventario
    disponibles = Herramienta.objects.filter(estado='DISPONIBLE', activo=True).count()
    prestadas   = Herramienta.objects.filter(estado='PRESTADA').count()
    reparacion  = Herramienta.objects.filter(estado='REPARACION').count()
    criticos    = Insumo.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).count()

    # Préstamos activos y vencidos
    prestamos_activos  = Prestamo.objects.filter(fecha_devolucion__isnull=True).select_related('alumno', 'herramienta', 'docente')
    prestamos_vencidos = [p for p in prestamos_activos if p.esta_vencido()]

    # Mantenimientos
    planes_vencidos = PlanMantenimiento.objects.filter(activo=True).select_related('herramienta')
    planes_vencidos = [p for p in planes_vencidos if p.esta_vencido()]
    planes_proximos = PlanMantenimiento.objects.filter(activo=True).select_related('herramienta')
    planes_proximos = [p for p in planes_proximos if p.esta_proximo()]

    # Reporte completo de préstamos ordenado por fecha de creación
    reporte_prestamos = Prestamo.objects.select_related(
        'alumno', 'herramienta', 'docente'
    ).order_by('-fecha_prestamo')

    # Agrupar préstamos por mes (últimos 6 meses):
    fecha_now = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    meses = []
    for offset in range(5, -1, -1):
        year = fecha_now.year
        month = fecha_now.month - offset
        while month <= 0:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        meses.append((year, month))

    inicio_mes = datetime(meses[0][0], meses[0][1], 1, 0, 0, 0)
    prestamos_por_mes = (
        Prestamo.objects
        .filter(fecha_prestamo__gte=inicio_mes)
        .annotate(mes=TruncMonth('fecha_prestamo'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    conteo_por_mes = {
        p['mes'].strftime('%Y-%m'): p['total']
        for p in prestamos_por_mes
    }

    labels = []
    datos  = []
    for year, month in meses:
        mes_dt = datetime(year, month, 1, 0, 0, 0)
        labels.append(mes_dt.strftime('%b %Y'))
        datos.append(conteo_por_mes.get(mes_dt.strftime('%Y-%m'), 0))

    context = {
        'disponibles':        disponibles,
        'prestadas':          prestadas,
        'reparacion':         reparacion,
        'criticos':           criticos,
        'prestamos_activos':  prestamos_activos.count(),
        'prestamos_vencidos': len(prestamos_vencidos),
        'planes_vencidos':    len(planes_vencidos),
        'planes_proximos':    len(planes_proximos),
        'lista_vencidos':     planes_vencidos[:5],
        'reporte_prestamos':  reporte_prestamos,
        'labels_grafico':     json.dumps(labels),
        'datos_grafico':      json.dumps(datos),
    }
    return context


def index(request):
    context = _get_reportes_context()
    return render(request, 'reportes/index.html', context)


def reportes(request):
    orden = request.GET.get('orden', 'desc')
    categoria_id = request.GET.get('categoria')

    queryset = Prestamo.objects.select_related(
        'alumno', 'herramienta', 'docente', 'herramienta__categoria'
    )

    if categoria_id:
        queryset = queryset.filter(herramienta__categoria_id=categoria_id)

    if orden == 'asc':
        queryset = queryset.order_by('fecha_prestamo')
    else:
        queryset = queryset.order_by('-fecha_prestamo')

    context = _get_reportes_context()
    context['reporte_prestamos'] = queryset
    context['categorias'] = Categoria.objects.all().order_by('nombre')
    context['categoria_actual'] = categoria_id or ''
    context['orden_actual'] = orden
    return render(request, 'reportes/reportes.html', context)

@login_required
def configuracion(request):
    config = ConfiguracionSistema.get()
    success = False

    if request.method == 'POST':
        form = ConfiguracionSistemaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            success = True
    else:
        form = ConfiguracionSistemaForm(instance=config)

    context = {
        'form': form,
        'success': success,
    }
    return render(request, 'reportes/configuracion.html', context)


@login_required
def categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    success = False

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = CategoriaForm()
    else:
        form = CategoriaForm()

    context = {
        'categorias': categorias,
        'form': form,
        'success': success,
    }
    return render(request, 'reportes/categorias.html', context)


@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('reportes:categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'reportes/editar_categoria.html', {'form': form, 'categoria': categoria})


@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('reportes:categorias')

    return render(request, 'reportes/confirmar_eliminar_categoria.html', {'categoria': categoria})


@login_required
def docentes(request):
    docentes = Docente.objects.filter(activo=True).order_by('apellido', 'nombre')
    success = False

    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = DocenteForm()
    else:
        form = DocenteForm()

    context = {
        'docentes': docentes,
        'form': form,
        'success': success,
    }
    return render(request, 'reportes/docentes.html', context)


@login_required
def editar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk, activo=True)

    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Docente actualizado correctamente.')
            return redirect('reportes:docentes')
    else:
        form = DocenteForm(instance=docente)

    return render(request, 'reportes/editar_docente.html', {'form': form, 'docente': docente})


@login_required
def eliminar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk, activo=True)

    if request.method == 'POST':
        docente.activo = False
        docente.save()
        messages.success(request, 'Docente eliminado correctamente.')
        return redirect('reportes:docentes')

    return render(request, 'reportes/confirmar_eliminar_docente.html', {'docente': docente})