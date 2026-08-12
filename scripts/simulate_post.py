import os
import django
import sys

# Asegurar que el proyecto esté en sys.path para poder importar el paquete settings
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panol_escolar.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Alumno, Herramienta, Docente, Prestamo

User = get_user_model()

c = Client()
user = User.objects.filter(is_active=True).first()
if not user:
    user = User.objects.create_user(username='testuser', password='testpass')

c.force_login(user)

al = Alumno.objects.filter(activo=True).first()
# Preferir herramienta disponible
h = Herramienta.objects.filter(activo=True, estado='DISPONIBLE').first()
if not h:
    h = Herramienta.objects.filter(activo=True).first()
d = Docente.objects.filter(activo=True).first()

print('Alumno:', getattr(al,'legajo',None))
print('Herramienta:', getattr(h,'codigo',None))
print('Docente pk:', getattr(d,'pk',None))

if not (al and h and d):
    print('Faltan datos de prueba: asegurate que existan Alumno, Herramienta y Docente activos.')
    sys.exit(2)

resp = c.post('/prestamos/nuevo/', {
    'alumno_qr': al.legajo,
    'herr_qr': h.codigo,
    'docente': d.pk,
    'observaciones': 'Prueba automatizada'
})

print('Status code:', resp.status_code)
print('Redirected:', resp.url if resp.status_code in (301,302) else '')

# imprimir parte de la respuesta HTML
try:
    content = resp.content.decode('utf-8')
except Exception:
    content = str(resp.content)

print('\n--- Response snippet ---')
print(content[:2000])

print('\nPrestamos activos para alumno/herramienta:')
print(Prestamo.objects.filter(alumno=al, herramienta=h, fecha_devolucion__isnull=True).count())


