import os
import csv  # <- Asegurado el import aquí
import qrcode
from io import BytesIO

from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
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
def editar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, activo=True)
    legajo_anterior = alumno.legajo # Guardamos el legajo viejo

    if request.method == 'POST':
        # Agregamos request.FILES por si el form tiene subida de archivos manuales
        form = AlumnoForm(request.POST, request.FILES, instance=alumno)
        if form.is_valid():
            alumno_guardado = form.save(commit=False)

            # Si el legajo cambia → eliminar QR viejo y generar uno nuevo
            if str(alumno_guardado.legajo) != str(legajo_anterior):
                if alumno.qr_code:
                    path = alumno.qr_code.path
                    if os.path.isfile(path):
                        os.remove(path)
                
                qr_img = qrcode.make(alumno_guardado.legajo)
                buffer = BytesIO()
                qr_img.save(buffer, format='PNG')
                alumno_guardado.qr_code.save(f'qr_{alumno_guardado.legajo}.png', File(buffer), save=False)

            alumno_guardado.save()
            messages.success(request, 'Alumno actualizado correctamente.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Editar Alumno'})


@login_required
def eliminar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, activo=True)
    
    if request.method == 'POST':
        # Validar que no tenga préstamos activos antes de borrar
        tiene_prestamos = Prestamo.objects.filter(
            alumno=alumno,
            fecha_devolucion__isnull=True
        ).exists()

        if tiene_prestamos:
            messages.error(request, 'No se puede dar de baja: el alumno tiene préstamos activos.')
            return redirect('alumnos:detalle', pk=alumno.pk)

        # Eliminar archivo físico del QR del disco
        if alumno.qr_code:
            path = alumno.qr_code.path
            if os.path.isfile(path):
                os.remove(path)
            alumno.qr_code = None

        # Baja lógica (Soft delete)
        alumno.activo = False
        alumno.save()
        messages.success(request, 'Alumno dado de baja del sistema.')
        return redirect('alumnos:lista')
        
    return render(request, 'alumnos/confirmar_eliminar.html', {'alumno': alumno})


@login_required
def exportar_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alumnos_proa.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Apellido', 'DNI', 'Curso', 'Email'])

    alumnos = Alumno.objects.filter(activo=True)
    for alumno in alumnos:
        writer.writerow([alumno.nombre, alumno.apellido, alumno.dni, alumno.curso, alumno.email])

    return response


@login_required
def importar_csv(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        csv_file = request.FILES['archivo_csv']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo debe tener extensión .csv')
            return redirect('alumnos:lista')

        try:
            cursos_validos = [curso[0] for curso in Alumno.CURSOS]
            
            # Decodificamos el archivo. Manejamos utf-8 por defecto.
            dataset = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(dataset)
            next(reader, None) # Saltar el encabezado

            creados = 0
            errores_curso = 0

            for row in reader:
                if len(row) >= 4:
                    nombre = row[0].strip()
                    apellido = row[1].strip()
                    dni = row[2].strip()
                    curso = row[3].strip()
                    email = row[4].strip() if len(row) > 4 else ''

                    if curso not in cursos_validos:
                        errores_curso += 1
                        continue 

                    # Chequeamos que no exista el DNI para evitar duplicados
                    if not Alumno.objects.filter(dni=dni).exists():
                        nuevo_alumno = Alumno(
                            nombre=nombre, 
                            apellido=apellido, 
                            dni=dni, 
                            curso=curso, 
                            email=email
                        )
                        nuevo_alumno.save()
                        
                        # Generamos el QR también en la importación masiva
                        qr_img = qrcode.make(nuevo_alumno.legajo)
                        buffer = BytesIO()
                        qr_img.save(buffer, format='PNG')
                        nuevo_alumno.qr_code.save(f'qr_{nuevo_alumno.legajo}.png', File(buffer), save=True)
                        
                        creados += 1
            
            if errores_curso > 0:
                messages.warning(request, f'Se importaron {creados} alumnos. Se omitieron {errores_curso} por tener un curso inválido.')
            else:
                messages.success(request, f'Se importaron {creados} alumnos correctamente.')
                
        except UnicodeDecodeError:
            messages.error(request, 'Error de codificación. Asegúrate de guardar el CSV con formato UTF-8.')
        except Exception as e:
            messages.error(request, 'Hubo un error al procesar el archivo. Verifica el formato.')
            
    return redirect('alumnos:lista')