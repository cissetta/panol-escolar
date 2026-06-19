"""
seed.py – Datos de prueba para el Sistema de Pañol Escolar
PROA Villa del Totoral – Programación IV 2026

Ejecutar con:
    python manage.py shell < seed.py
    o en powershell
    Get-Content seed.py | python manage.py shell

O desde el manage.py:
    python manage.py runscript seed   (requiere django-extensions)

Crea datos de prueba para que cada grupo pueda trabajar
su módulo sin depender de que otro grupo termine primero.
"""

from django.contrib.auth.models import User
from core.models import (
    ConfiguracionSistema, Perfil, Docente, Alumno,
    Categoria, Herramienta, Insumo,
    Prestamo, PlanMantenimiento, TareaMantenimiento,
    LogHerramienta
)
from django.utils import timezone
from datetime import date, timedelta

print("🌱 Iniciando carga de datos de prueba...")

# ── Configuración del sistema ────────────────────────────────────
config = ConfiguracionSistema.get()
config.nombre_institucion       = 'PROA Villa del Totoral'
config.dias_maximo_prestamo     = 2
config.dias_aviso_mantenimiento = 7
config.save()
print("✅ Configuración del sistema")

# ── Usuarios y roles ─────────────────────────────────────────────
def crear_usuario(username, password, email, rol, first_name='', last_name=''):
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email, 'first_name': first_name, 'last_name': last_name
    })
    if created:
        user.set_password(password)
        user.save()
    perfil, _ = Perfil.objects.get_or_create(user=user, defaults={'rol': rol})
    return user

crear_usuario('admin',     'admin123',     'admin@proa.edu.ar',          'ADMIN',    'Admin',    'Sistema')
crear_usuario('panolero',  'panolero123',  'garcia@proa.edu.ar',         'PANOLERO', 'Roberto',  'García')
crear_usuario('martinez',  'docente123',   'martinez@proa.edu.ar',       'DOCENTE',  'Carlos',   'Martínez')
crear_usuario('lopez',     'docente123',   'lopez@proa.edu.ar',          'DOCENTE',  'Ana',      'López')
crear_usuario('gonzalez',  'alumno123',    'lgonzalez@proa.edu.ar',      'ALUMNO',   'Lucas',    'González')
print("✅ Usuarios creados (admin / panolero / martinez / lopez / gonzalez)")
print("   Contraseñas: admin123, panolero123, docente123, alumno123")

# ── Docentes ─────────────────────────────────────────────────────
doc_martinez, _ = Docente.objects.get_or_create(email='martinez@proa.edu.ar', defaults={
    'nombre': 'Carlos', 'apellido': 'Martínez'
})
doc_lopez, _ = Docente.objects.get_or_create(email='lopez@proa.edu.ar', defaults={
    'nombre': 'Ana', 'apellido': 'López'
})
doc_fernandez, _ = Docente.objects.get_or_create(email='fernandez@proa.edu.ar', defaults={
    'nombre': 'Marcelo', 'apellido': 'Fernández'
})
print("✅ Docentes: Martínez, López, Fernández")

# ── Alumnos ──────────────────────────────────────────────────────
alumnos_data = [
    ('Lucas',    'González',  '44123456', '3A', 'lgonzalez@proa.edu.ar'),
    ('Martina',  'Pérez',     '44987654', '3A', 'mperez@proa.edu.ar'),
    ('Federico', 'Rodríguez', '45111222', '3B', 'frodriguez@proa.edu.ar'),
    ('Ana',      'Fernández', '45333444', '3B', 'afernandez@proa.edu.ar'),
    ('Santiago', 'López',     '45555666', '4A', 'slopez@proa.edu.ar'),
    ('Valentina','Torres',    '45777888', '4A', 'vtorres@proa.edu.ar'),
    ('Mateo',    'Díaz',      '45999000', '4B', 'mdiaz@proa.edu.ar'),
    ('Camila',   'Ruiz',      '46111333', '4B', 'cruiz@proa.edu.ar'),
]
alumnos = []
for nombre, apellido, dni, curso, email in alumnos_data:
    a, created = Alumno.objects.get_or_create(dni=dni, defaults={
        'nombre': nombre, 'apellido': apellido, 'curso': curso, 'email': email
    })
    alumnos.append(a)
print(f"✅ {len(alumnos)} alumnos creados")

# ── Categorías ───────────────────────────────────────────────────
cats = {}
categorias_data = [
    ('Electrónica',     '#2E86DE'),
    ('Mecánica',        '#27AE60'),
    ('Madera',          '#E67E22'),
    ('Metalmecánica',   '#C0392B'),
    ('Construcción',    '#8E44AD'),
    ('Medición',        '#16A085'),
]
for nombre, color in categorias_data:
    c, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={'color_hex': color})
    cats[nombre] = c
print(f"✅ {len(cats)} categorías")

# ── Herramientas ─────────────────────────────────────────────────
herramientas_data = [
    ('Multímetro digital #01',      'Electrónica',   'Estante A-1', 'DISPONIBLE', 'Fluke', '179'),
    ('Multímetro digital #02',      'Electrónica',   'Estante A-1', 'DISPONIBLE', 'Fluke', '179'),
    ('Multímetro digital #03',      'Electrónica',   'Estante A-1', 'PRESTADA',   'Fluke', '179'),
    ('Cautín 40W #01',              'Electrónica',   'Estante A-2', 'DISPONIBLE', 'Weller', 'WE1010'),
    ('Cautín 40W #02',              'Electrónica',   'Estante A-2', 'PRESTADA',   'Weller', 'WE1010'),
    ('Cautín 40W #03',              'Electrónica',   'Estante A-2', 'DISPONIBLE', 'Weller', 'WE1010'),
    ('Taladro inalámbrico #01',     'Mecánica',      'Estante B-1', 'DISPONIBLE', 'Bosch', 'GSB 18V'),
    ('Taladro inalámbrico #02',     'Mecánica',      'Estante B-1', 'PRESTADA',   'Bosch', 'GSB 18V'),
    ('Taladro de banco #01',        'Mecánica',      'Estante D-1', 'DISPONIBLE', 'Gamma', 'G19010AR'),
    ('Sierra caladora #01',         'Madera',        'Estante C-1', 'DISPONIBLE', 'Black&Decker', 'KS701'),
    ('Sierra caladora #02',         'Madera',        'Estante C-1', 'REPARACION', 'Black&Decker', 'KS701'),
    ('Amoladora angular #01',       'Metalmecánica', 'Estante B-2', 'DISPONIBLE', 'Dewalt', 'DWE402'),
    ('Amoladora angular #02',       'Metalmecánica', 'Estante B-2', 'DISPONIBLE', 'Dewalt', 'DWE402'),
    ('Soldadora MIG',               'Metalmecánica', 'Estante E-1', 'REPARACION', 'Lincoln', 'Easy MIG'),
    ('Compresor de aire',           'Mecánica',      'Estante E-2', 'DISPONIBLE', 'Stanley', 'D200/6/8'),
    ('Juego de llaves allen',       'Medición',      'Cajón A-1',   'DISPONIBLE', 'Stanley', 'STMT73596'),
    ('Destornilladores Phillips x5','Mecánica',      'Cajón A-2',   'DISPONIBLE', 'Stanley', 'STHT60038'),
    ('Nivel digital',               'Medición',      'Cajón B-1',   'DISPONIBLE', 'Bosch', 'GTL 3'),
    ('Pinza amperímetrica',         'Medición',      'Estante A-3', 'DISPONIBLE', 'Fluke', '323'),
    ('Fuente de alimentación',      'Electrónica',   'Estante A-4', 'BAJA',       'Minipa', 'MLP-3305'),
]
herramientas = []
for nombre, cat, ubi, estado, marca, modelo in herramientas_data:
    h, created = Herramienta.objects.get_or_create(nombre=nombre, defaults={
        'categoria': cats.get(cat), 'ubicacion': ubi, 'estado': estado,
        'marca': marca, 'modelo': modelo,
        'fecha_compra': date(2024, 3, 15)
    })
    herramientas.append(h)
    if created:
        LogHerramienta.objects.create(
            herramienta=h, tipo='ALTA',
            descripcion=f'Incorporación al inventario. Marca: {marca}, Modelo: {modelo}'
        )
print(f"✅ {len(herramientas)} herramientas")

# ── Insumos ──────────────────────────────────────────────────────
insumos_data = [
    ('Estaño para soldar 1mm', 'Electrónica', 'metros',  45.0, 20.0),
    ('Pasta de soldar',        'Electrónica', 'gramos',   2.0, 10.0),
    ('Cinta aisladora negra',  'Electrónica', 'rollos',  12.0,  5.0),
    ('Lija 120 grano',         'Madera',      'hojas',    8.0, 15.0),
    ('Lija 220 grano',         'Madera',      'hojas',   20.0, 10.0),
    ('Broca HSS 6mm',          'Mecánica',    'unidades', 3.0, 10.0),
    ('Broca HSS 8mm',          'Mecánica',    'unidades', 7.0,  5.0),
    ('Disco de corte 4.5"',    'Metalmecánica','unidades',15.0, 10.0),
    ('Disco de desbaste 4.5"', 'Metalmecánica','unidades', 5.0,  8.0),
    ('Silicona blanca',        'Construcción','unidades',  4.0,  3.0),
]
from core.models import Insumo
for nombre, cat, unidad, stock_actual, stock_minimo in insumos_data:
    Insumo.objects.get_or_create(nombre=nombre, defaults={
        'categoria': cats.get(cat), 'unidad': unidad,
        'stock_actual': stock_actual, 'stock_minimo': stock_minimo
    })
print("✅ 10 insumos")

# ── Préstamos activos ─────────────────────────────────────────────
# Multímetro #03 prestado a González
h_multi3    = Herramienta.objects.get(nombre='Multímetro digital #03')
h_cautin2   = Herramienta.objects.get(nombre='Cautín 40W #02')
h_taladro2  = Herramienta.objects.get(nombre='Taladro inalámbrico #02')
al_gonzalez = alumnos[0]
al_perez    = alumnos[1]
al_lopez    = alumnos[4]

p1, _ = Prestamo.objects.get_or_create(
    alumno=al_gonzalez, herramienta=h_multi3, fecha_devolucion__isnull=True,
    defaults={'docente': doc_martinez, 'fecha_prestamo': timezone.now() - timedelta(hours=3)}
)
p2, _ = Prestamo.objects.get_or_create(
    alumno=al_perez, herramienta=h_cautin2, fecha_devolucion__isnull=True,
    defaults={'docente': doc_martinez, 'fecha_prestamo': timezone.now() - timedelta(hours=2)}
)
# Préstamo vencido (más de 2 días)
p3, _ = Prestamo.objects.get_or_create(
    alumno=al_lopez, herramienta=h_taladro2, fecha_devolucion__isnull=True,
    defaults={'docente': doc_lopez, 'fecha_prestamo': timezone.now() - timedelta(days=3)}
)
print("✅ 3 préstamos activos (uno vencido para probar alertas)")

# ── Planes de mantenimiento ───────────────────────────────────────
h_banco     = Herramienta.objects.get(nombre='Taladro de banco #01')
h_compresor = Herramienta.objects.get(nombre='Compresor de aire')
h_sierra2   = Herramienta.objects.get(nombre='Sierra caladora #02')
h_soldadora = Herramienta.objects.get(nombre='Soldadora MIG')

plan1, _ = PlanMantenimiento.objects.get_or_create(
    nombre='Mantenimiento mensual – Taladro de banco',
    defaults={
        'herramienta': h_banco, 'tipo': 'PREV',
        'descripcion': 'Limpieza, lubricación y revisión de seguridad mensual.',
        'frecuencia_dias': 30,
        'proxima_ejecucion': date.today() - timedelta(days=8)  # vencido
    }
)
for desc, resp, orden in [
    ('Limpiar filtro de aire',       'Pañolero',        1),
    ('Lubricar columna y mesa',      'Pañolero',        2),
    ('Verificar tensión de correa',  'Docente de taller', 3),
    ('Probar seguro de encendido',   'Docente de taller', 4),
]:
    TareaMantenimiento.objects.get_or_create(plan=plan1, descripcion=desc,
        defaults={'responsable': resp, 'orden': orden})

plan2, _ = PlanMantenimiento.objects.get_or_create(
    nombre='Mantenimiento mensual – Compresor',
    defaults={
        'herramienta': h_compresor, 'tipo': 'PREV',
        'descripcion': 'Drenaje del condensador, revisión de válvulas y filtros.',
        'frecuencia_dias': 30,
        'proxima_ejecucion': date.today() - timedelta(days=3)  # vencido
    }
)

plan3, _ = PlanMantenimiento.objects.get_or_create(
    nombre='Reparación sierra caladora #02',
    defaults={
        'herramienta': h_sierra2, 'tipo': 'CORR',
        'descripcion': 'Reemplazo de hoja guía y revisión del motor.',
        'proxima_ejecucion': date.today() + timedelta(days=2)  # próximo
    }
)

plan4, _ = PlanMantenimiento.objects.get_or_create(
    nombre='Mantenimiento trimestral – Soldadora MIG',
    defaults={
        'herramienta': h_soldadora, 'tipo': 'PREV',
        'descripcion': 'Limpieza de tobera, revisión de cable y antorcha.',
        'frecuencia_dias': 90,
        'proxima_ejecucion': date.today() + timedelta(days=45)  # al día
    }
)
print("✅ 4 planes de mantenimiento (2 vencidos, 1 próximo, 1 al día)")

print()
print("═" * 55)
print("🎉 Datos de prueba cargados correctamente")
print("═" * 55)
print()
print("Usuarios disponibles:")
print("  admin      / admin123     → Administrador")
print("  panolero   / panolero123  → Pañolero")
print("  martinez   / docente123   → Docente")
print("  lopez      / docente123   → Docente")
print("  gonzalez   / alumno123    → Alumno")
print()
print("Estado inicial del inventario:")
print("  Herramientas disponibles : 14")
print("  Herramientas prestadas   :  3  (una vencida > 2 días)")
print("  En reparación            :  2")
print("  Baja                     :  1")
print("  Insumos con stock crítico:  3")
