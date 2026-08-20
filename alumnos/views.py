# Grupo 2 – Inventario
# TODO: implementar las vistas de este módulo
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse

# Asegurate de importar Prestamo también para las validaciones
from core.models import Alumno, Prestamo 
from .forms import AlumnoForm


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    alumnos_qs = Alumno.objects.filter(activo=True)
    
    if q:
        alumnos_qs = alumnos_qs.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(dni__icontains=q) |
            Q(curso__icontains=q)
        )
    alumnos_qs = alumnos_qs.order_by('apellido', 'nombre')
    
    paginator = Paginator(alumnos_qs, 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'alumnos/lista.html', {'page_obj': page_obj, 'q': q})


@login_required
def detalle(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, activo=True)
    prestamos = alumno.prestamo_set.all().order_by('-fecha_prestamo')
    
    return render(request, 'alumnos/detalle.html', {
        'alumno': alumno, 
        'prestamos': prestamos
    })


@login_required
def nuevo(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save() 
            
            # Generar QR automáticamente al guardar
            qr_img = qrcode.make(alumno.legajo)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            alumno.qr_code.save(f'qr_{alumno.legajo}.png', File(buffer), save=True)
            
            messages.success(request, 'Alumno creado correctamente con su código QR.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Nuevo Alumno'})


@login_required
def index(request):
    """Vista principal del módulo – reemplazar con la implementación real."""
    return render(request, 'inventario/index.html')
