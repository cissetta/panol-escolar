# Grupo 5 – Reportes y Dashboard
# TODO: implementar las vistas de este módulo
import json
from django import forms
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F
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

@login_required
def index(request):
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

    # Últimos préstamos
    ultimos_prestamos = Prestamo.objects.select_related(
        'alumno', 'herramienta', 'docente'
    ).order_by('-fecha_prestamo')[:8]

    # Agrupar préstamos por mes (últimos 6 meses):
    prestamos_por_mes = (
        Prestamo.objects
        .annotate(mes=TruncMonth('fecha_prestamo'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels = [p['mes'].strftime('%b %Y') for p in prestamos_por_mes]
    datos  = [p['total'] for p in prestamos_por_mes]

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
        'ultimos_prestamos':  ultimos_prestamos,
        'labels_grafico':     json.dumps(labels),
        'datos_grafico':      json.dumps(datos),
    }
    return render(request, 'reportes/index.html', context)

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
def docentes(request):
    docentes = Docente.objects.all().order_by('apellido', 'nombre')
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