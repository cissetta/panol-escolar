from io import BytesIO

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import solo_panolero, solo_docente
from core.models import Alumno, Prestamo

from .forms import AlumnoForm


@solo_docente
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
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'alumnos/lista.html', {'page_obj': page_obj, 'q': q})


@solo_docente
def detalle(request, pk):
    alumno   = get_object_or_404(Alumno, pk=pk)
    prestamos = alumno.prestamo_set.all().order_by('-fecha_prestamo')
    return render(request, 'alumnos/detalle.html', {
        'alumno': alumno,
        'prestamos': prestamos,
    })


@solo_panolero
def nuevo(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save()
            # Generar QR automáticamente
            qr_img = qrcode.make(alumno.legajo)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            alumno.qr_code.save(f'qr_{alumno.legajo}.png', File(buffer), save=True)
            messages.success(request, f'Alumno {alumno} creado con código QR.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Nuevo Alumno'})


@solo_panolero
def editar(request, pk):
    alumno      = get_object_or_404(Alumno, pk=pk)
    legajo_prev = alumno.legajo

    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            alumno = form.save()
            # Si cambió el legajo, regenerar QR
            if alumno.legajo != legajo_prev:
                import os
                if alumno.qr_code and os.path.isfile(alumno.qr_code.path):
                    os.remove(alumno.qr_code.path)
                qr_img = qrcode.make(alumno.legajo)
                buffer = BytesIO()
                qr_img.save(buffer, format='PNG')
                alumno.qr_code.save(f'qr_{alumno.legajo}.png', File(buffer), save=True)
            messages.success(request, f'Alumno {alumno} actualizado.')
            return redirect('alumnos:detalle', pk=alumno.pk)
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Editar Alumno', 'alumno': alumno})


@solo_panolero
def confirmar_eliminar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    if request.method == 'POST':
        # Validar que no tenga préstamos activos
        if Prestamo.objects.filter(alumno=alumno, fecha_devolucion__isnull=True).exists():
            messages.error(request, 'No se puede dar de baja: el alumno tiene préstamos activos.')
            return redirect('alumnos:detalle', pk=alumno.pk)

        # Eliminar QR del disco
        import os
        if alumno.qr_code:
            path = alumno.qr_code.path
            if os.path.isfile(path):
                os.remove(path)
            alumno.qr_code = None

        alumno.activo = False
        alumno.save()
        messages.success(request, f'Alumno {alumno} dado de baja correctamente.')
        return redirect('alumnos:lista')

    return render(request, 'alumnos/confirmar_eliminar.html', {'alumno': alumno})


from django.http import HttpResponseForbidden

def _generar_qr(alumno):
    """Genera y guarda el QR de un alumno."""
    qr_img = qrcode.make(alumno.legajo)
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    alumno.qr_code.save(f'qr_{alumno.legajo}.png', File(buffer), save=True)


@solo_panolero
def reactivar(request, pk):
    """Solo ADMIN puede reactivar un alumno inactivo."""
    if getattr(getattr(request.user, 'perfil', None), 'rol', None) != 'ADMIN':
        return HttpResponseForbidden('Solo los administradores pueden reactivar alumnos.')
    alumno = get_object_or_404(Alumno, pk=pk, activo=False)
    if request.method == 'POST':
        alumno.activo = True
        alumno.save()
        if not alumno.qr_code:
            _generar_qr(alumno)
        messages.success(request, f'Alumno {alumno} reactivado correctamente.')
        return redirect('alumnos:detalle', pk=alumno.pk)
    return render(request, 'alumnos/confirmar_reactivar.html', {'alumno': alumno})


@solo_panolero
def eliminar_definitivo(request, pk):
    """Solo ADMIN. Solo si el alumno está inactivo y sin historial de préstamos."""
    if getattr(getattr(request.user, 'perfil', None), 'rol', None) != 'ADMIN':
        return HttpResponseForbidden('Solo los administradores pueden eliminar alumnos definitivamente.')
    alumno = get_object_or_404(Alumno, pk=pk, activo=False)
    if request.method == 'POST':
        if alumno.prestamo_set.exists():
            messages.error(request,
                'No se puede eliminar: el alumno tiene historial de préstamos. '
                'Solo se pueden eliminar alumnos sin ningún préstamo registrado.')
            return redirect('alumnos:detalle', pk=alumno.pk)
        import os
        if alumno.qr_code:
            path = alumno.qr_code.path
            if os.path.isfile(path):
                os.remove(path)
        alumno.delete()
        messages.success(request, 'Alumno eliminado definitivamente del sistema.')
        return redirect('alumnos:lista')
    return render(request, 'alumnos/confirmar_eliminar_definitivo.html', {'alumno': alumno})


import csv
from django.http import HttpResponse

@solo_docente
def exportar_csv(request):
    """Exporta el listado de alumnos activos a CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alumnos.csv"'
    writer = csv.writer(response)
    writer.writerow(['Legajo', 'Apellido', 'Nombre', 'DNI', 'Curso', 'Email'])
    for a in Alumno.objects.filter(activo=True).order_by('apellido', 'nombre'):
        writer.writerow([a.legajo, a.apellido, a.nombre, a.dni, a.curso, a.email])
    return response


@solo_panolero
def importar_csv(request):
    """TODO (Grupo 1): implementar importación de alumnos desde CSV."""
    messages.info(request, 'Importación CSV — funcionalidad pendiente de implementar.')
    return redirect('alumnos:lista')
