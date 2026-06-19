from django.contrib import admin
from .models import (
    ConfiguracionSistema, Docente, Alumno, Categoria,
    Herramienta, LogHerramienta, Insumo, MovimientoInsumo,
    Prestamo, PrestamoInsumo,
    PlanMantenimiento, TareaMantenimiento, EjecucionMantenimiento,
)

admin.site.site_header = 'Sistema de Pañol – PROA Villa del Totoral'
admin.site.site_title  = 'Pañol Admin'
admin.site.index_title = 'Panel de Administración'


@admin.register(ConfiguracionSistema)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['nombre_institucion', 'dias_maximo_prestamo', 'dias_aviso_mantenimiento']


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display  = ['apellido', 'nombre', 'email', 'activo']
    list_filter   = ['activo']
    search_fields = ['nombre', 'apellido', 'email']


class LogHerramientaInline(admin.TabularInline):
    model   = LogHerramienta
    extra   = 0
    readonly_fields = ['tipo', 'descripcion', 'fecha', 'usuario']
    can_delete = False


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display  = ['legajo', 'apellido', 'nombre', 'dni', 'curso', 'activo']
    list_filter   = ['curso', 'activo']
    search_fields = ['nombre', 'apellido', 'dni', 'legajo']
    readonly_fields = ['legajo', 'fecha_alta']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color_hex']


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display  = ['codigo', 'nombre', 'categoria', 'ubicacion', 'estado']
    list_filter   = ['estado', 'categoria']
    search_fields = ['nombre', 'codigo', 'marca']
    readonly_fields = ['codigo', 'fecha_alta']
    inlines = [LogHerramientaInline]


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display  = ['codigo', 'nombre', 'stock_actual', 'stock_minimo', 'unidad', 'es_critico']
    list_filter   = ['categoria']
    search_fields = ['nombre', 'codigo']
    readonly_fields = ['codigo']

    @admin.display(boolean=True, description='Stock crítico')
    def es_critico(self, obj):
        return obj.es_critico


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display  = ['alumno', 'herramienta', 'docente', 'fecha_prestamo', 'fecha_devolucion']
    list_filter   = ['fecha_prestamo', 'docente']
    search_fields = ['alumno__nombre', 'alumno__apellido', 'herramienta__nombre']
    readonly_fields = ['fecha_prestamo']


@admin.register(PlanMantenimiento)
class PlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'herramienta', 'tipo', 'proxima_ejecucion', 'activo']
    list_filter  = ['tipo', 'activo']

admin.site.register(LogHerramienta)
admin.site.register(MovimientoInsumo)
admin.site.register(PrestamoInsumo)
admin.site.register(TareaMantenimiento)
admin.site.register(EjecucionMantenimiento)
