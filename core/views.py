from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F
from .models import Herramienta, Insumo, Prestamo, PlanMantenimiento, ConfiguracionSistema


INSUMO_CATEGORIAS = [
    ('Insumos energéticos', '#34495E'),
    ('Insumos digitales', '#F39C12'),
    ('Insumos logísticos', '#7F8C8D'),
]

def asegurar_categorias_insumos():
    for nombre in ['Herramienta', 'Maquina']:
        Categoria.objects.filter(nombre__iexact=nombre).delete()

    for nombre, color in INSUMO_CATEGORIAS:
        Categoria.objects.get_or_create(nombre=nombre, defaults={'color_hex': color})


def generar_qr_herramienta(herramienta):
    if not herramienta.codigo:
        return

    if herramienta.qr_code:
        herramienta.qr_code.delete(save=False)

    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(herramienta.codigo)
    qr.make(fit=True)
    imagen = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    imagen.save(buffer, format='PNG')
    buffer.seek(0)

    nombre_archivo = f'qr/herramientas/{herramienta.codigo}.png'
    herramienta.qr_code.save(nombre_archivo, ContentFile(buffer.getvalue()), save=False)
    herramienta.save(update_fields=['qr_code'])




@login_required
def dashboard(request):
    config = ConfiguracionSistema.get()

    # Indicadores de inventario
    disponibles = Herramienta.objects.filter(estado='DISPONIBLE', activo=True).count()
    prestadas   = Herramienta.objects.filter(estado='PRESTADA').count()
    reparacion  = Herramienta.objects.filter(estado='REPARACION').count()
    criticos    = Insumo.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).count()

    # Préstamos activos y vencidos
    prestamos_activos  = Prestamo.objects.filter(fecha_devolucion__isnull=True).select_related('alumno', 'herramienta', 'docente')
    prestamos_vencidos = [p for p in prestamos_activos if p.esta_vencido()]

    # Mantenimientos
    planes_vencidos  = PlanMantenimiento.objects.filter(activo=True).select_related('herramienta')
    planes_vencidos  = [p for p in planes_vencidos if p.esta_vencido()]
    planes_proximos  = PlanMantenimiento.objects.filter(activo=True).select_related('herramienta')
    planes_proximos  = [p for p in planes_proximos if p.esta_proximo()]

    # Últimos préstamos
    ultimos_prestamos = Prestamo.objects.select_related(
        'alumno', 'herramienta', 'docente'
    ).order_by('-fecha_prestamo')[:8]

    context = {
        'disponibles':      disponibles,
        'prestadas':        prestadas,
        'reparacion':       reparacion,
        'criticos':         criticos,
        'prestamos_activos': prestamos_activos.count(),
        'prestamos_vencidos': len(prestamos_vencidos),
        'planes_vencidos':  len(planes_vencidos),
        'planes_proximos':  len(planes_proximos),
        'lista_vencidos':   planes_vencidos[:5],
        'ultimos_prestamos': ultimos_prestamos,
    }
    return render(request, 'core/dashboard.html', context)
