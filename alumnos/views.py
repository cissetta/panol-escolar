import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date
from core.models import Alumno
from .forms import AlumnoForm
from .utils import generar_qr_alumno
from django.http import HttpResponse
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
@login_required
def nuevo(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            
            # ¡Ya no necesitamos generar el legajo ni la fecha aquí! 
            # El modelo lo hará solo al ejecutar save()
            alumno.save() 
            
            # Ahora que se guardó y tiene legajo, generamos el QR
            generar_qr_alumno(alumno)
            alumno.save() # Guardamos por segunda vez para actualizar el QR
            
            messages.success(request, 'Alumno creado correctamente.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Nuevo Alumno / Editar'})
def editar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, activo=True)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, request.FILES, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumno actualizado correctamente.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/form.html', {'form': form, 'accion': 'Nuevo Alumno / Editar'})

@login_required
def eliminar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, activo=True)
    if request.method == 'POST':
        alumno.activo = False
        alumno.save()
        messages.success(request, 'Alumno dado de baja.')
        return redirect('alumnos:lista')
    return render(request, 'alumnos/confirmar_eliminar.html', {'alumno': alumno})
@login_required
def exportar_csv(request):
    # Configuramos la respuesta para que el navegador sepa que es un archivo descargable
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alumnos_proa.csv"'

    writer = csv.writer(response)
    # Escribimos los encabezados de las columnas
    writer.writerow(['Nombre', 'Apellido', 'DNI', 'Curso', 'Email'])

    # Obtenemos los alumnos activos y los escribimos fila por fila
    alumnos = Alumno.objects.filter(activo=True)
    for alumno in alumnos:
        writer.writerow([alumno.nombre, alumno.apellido, alumno.dni, alumno.curso, alumno.email])

    return response

@login_required
@login_required
def importar_csv(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        csv_file = request.FILES['archivo_csv']

        # Verificamos que sea un archivo .csv
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo debe tener extensión .csv')
            return redirect('alumnos:lista')

        try:
            # Obtenemos la lista de cursos válidos directamente del modelo (ej: ['3A', '3B', ...])
            cursos_validos = [curso[0] for curso in Alumno.CURSOS]

            dataset = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(dataset)
            next(reader, None)  # Saltamos la primera fila (los encabezados)

            creados = 0
            errores_curso = 0

            for row in reader:
                if len(row) >= 4:
                    nombre = row[0].strip()
                    apellido = row[1].strip()
                    dni = row[2].strip()
                    curso = row[3].strip()
                    email = row[4].strip() if len(row) > 4 else ''

                    # Validamos que el curso ingresado exista en el sistema
                    if curso not in cursos_validos:
                        errores_curso += 1
                        continue  # Saltamos este alumno y pasamos al siguiente

                    # Creamos el alumno si el DNI no existe
                    if not Alumno.objects.filter(dni=dni).exists():
                        nuevo_alumno = Alumno(
                            nombre=nombre, 
                            apellido=apellido, 
                            dni=dni, 
                            curso=curso, 
                            email=email
                        )
                        nuevo_alumno.save()
                        
                        from .utils import generar_qr_alumno
                        generar_qr_alumno(nuevo_alumno)
                        nuevo_alumno.save()
                        
                        creados += 1
            
            # Mensaje final detallado
            if errores_curso > 0:
                messages.warning(request, f'Se importaron {creados} alumnos. Se omitieron {errores_curso} por tener un curso inválido.')
            else:
                messages.success(request, f'Se importaron {creados} alumnos correctamente.')
                
        except Exception as e:
            messages.error(request, 'Hubo un error al procesar el archivo. Verifica el formato.')
            
    return redirect('alumnos:lista')