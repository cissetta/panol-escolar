# -*- coding: utf-8 -*-
"""
seed_presentacion.py – Datos completos para presentación al cliente
PROA Villa del Totoral – Programación IV 2026

Carga:
  • 200 alumnos (20 por curso, 10 cursos: 3A-7B)
  • 22 docentes + 2 pañoleros + admin
  • ~80 herramientas de mano + máquinas completas del taller
  • 20 insumos
  • 12 préstamos en distintos estados
  • 10 planes de mantenimiento cubriendo todos los casos de uso

Ejecutar con:
    Linux/Mac:   python manage.py shell < seed_presentacion.py

    Windows (PowerShell) — IMPORTANTE: usar esta forma para preservar acentos:
    python manage.py shell --command="exec(open('seed_presentacion.py', encoding='utf-8').read())"
"""

import random
from django.contrib.auth.models import User
from accounts.models import Perfil
from core.models import (
    ConfiguracionSistema, Docente, Alumno,
    Categoria, Herramienta, Insumo, MovimientoInsumo,
    Prestamo, PlanMantenimiento, TareaMantenimiento,
    EjecucionMantenimiento, LogHerramienta,
)
from django.utils import timezone
from datetime import date, timedelta

print("🌱 Iniciando seed de presentación...")

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DEL SISTEMA
# ══════════════════════════════════════════════════════════════════
config = ConfiguracionSistema.get()
config.nombre_institucion       = 'PROA Villa del Totoral'
config.dias_maximo_prestamo     = 2
config.dias_aviso_mantenimiento = 7
config.email_alertas            = 'panol.proa.totoral@gmail.com'
config.save()
print("✅ Configuración del sistema")


# ══════════════════════════════════════════════════════════════════
#  HELPER: crear usuario
# ══════════════════════════════════════════════════════════════════
def crear_usuario(username, password, email, rol, first_name='', last_name=''):
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email, 'first_name': first_name, 'last_name': last_name
    })
    if created:
        user.set_password(password)
        user.save()
    Perfil.objects.get_or_create(user=user, defaults={'rol': rol})
    return user

# ══════════════════════════════════════════════════════════════════
#  USUARIOS DEL SISTEMA
# ══════════════════════════════════════════════════════════════════
crear_usuario('admin',      'admin123',      'admin@proa.edu.ar',          'ADMIN',    'Cristian', 'Issetta')
crear_usuario('panolero1',  'panolero123',   'garcia@proa.edu.ar',         'PANOLERO', 'Roberto',  'García')
crear_usuario('panolero2',  'panolero123',   'salinas@proa.edu.ar',        'PANOLERO', 'Mariela',  'Salinas')
crear_usuario('martinez',   'docente123',    'martinez@proa.edu.ar',       'DOCENTE',  'Carlos',   'Martínez')
crear_usuario('lopez',      'docente123',    'lopez@proa.edu.ar',          'DOCENTE',  'Ana',      'López')
crear_usuario('fernandez',  'docente123',    'fernandez@proa.edu.ar',      'DOCENTE',  'Marcelo',  'Fernández')
crear_usuario('alumno1',    'alumno123',     'lgonzalez@proa.edu.ar',      'ALUMNO',   'Lucas',    'González')
print("✅ Usuarios: admin / panolero1 / panolero2 / martinez / lopez / fernandez / alumno1")
print("   Contraseñas: admin123, panolero123, docente123, alumno123")


# ══════════════════════════════════════════════════════════════════
#  DOCENTES (22)
# ══════════════════════════════════════════════════════════════════
docentes_data = [
    ('Carlos',    'Martínez',  'martinez@proa.edu.ar'),
    ('Ana',       'López',     'lopez@proa.edu.ar'),
    ('Marcelo',   'Fernández', 'fernandez@proa.edu.ar'),
    ('Graciela',  'Soria',     'gsoria@proa.edu.ar'),
    ('Héctor',    'Ramos',     'hramos@proa.edu.ar'),
    ('Patricia',  'Villalba',  'pvillalba@proa.edu.ar'),
    ('Daniel',    'Acosta',    'dacosta@proa.edu.ar'),
    ('Silvia',    'Moreno',    'smoreno@proa.edu.ar'),
    ('Ricardo',   'Peralta',   'rperalta@proa.edu.ar'),
    ('Verónica',  'Castro',    'vcastro@proa.edu.ar'),
    ('Gustavo',   'Herrera',   'gherrera@proa.edu.ar'),
    ('Claudia',   'Vega',      'cvega@proa.edu.ar'),
    ('Osvaldo',   'Díaz',      'odiaz@proa.edu.ar'),
    ('Mónica',    'Ruiz',      'mruiz@proa.edu.ar'),
    ('Jorge',     'Álvarez',   'jalvarez@proa.edu.ar'),
    ('Susana',    'Medina',    'smedina@proa.edu.ar'),
    ('Fabián',    'Ríos',      'frios@proa.edu.ar'),
    ('Liliana',   'Cabrera',   'lcabrera@proa.edu.ar'),
    ('Alejandro', 'Suárez',    'asuarez@proa.edu.ar'),
    ('Cristina',  'Molina',    'cmolina@proa.edu.ar'),
    ('Rodolfo',   'Vargas',    'rvargas@proa.edu.ar'),
    ('Norma',     'Flores',    'nflores@proa.edu.ar'),
]
docentes = []
for nombre, apellido, email in docentes_data:
    d, _ = Docente.objects.get_or_create(email=email, defaults={
        'nombre': nombre, 'apellido': apellido
    })
    docentes.append(d)
print(f"✅ {len(docentes)} docentes")


# ══════════════════════════════════════════════════════════════════
#  ALUMNOS (20 por curso × 10 cursos = 200)
# ══════════════════════════════════════════════════════════════════
nombres_v = ['Valentina','Camila','Martina','Sofía','Lucía','Florencia','Agustina',
             'Micaela','Natalia','Romina','Aldana','Rocío','Brenda','Daiana','Noelia',
             'Cintia','Antonella','Julieta','Milagros','Nadia']
nombres_m = ['Lucas','Mateo','Santiago','Sebastián','Nicolás','Agustín','Facundo',
             'Tomás','Rodrigo','Ezequiel','Ignacio','Ramiro','Leandro','Gonzalo',
             'Diego','Franco','Lautaro','Axel','Kevin','Joaquín']
apellidos = ['González','Rodríguez','García','Fernández','López','Martínez','Pérez',
             'Sánchez','Romero','Torres','Díaz','Álvarez','Ruiz','Morales','Giménez',
             'Herrera','Medina','Castro','Flores','Vega']

cursos = ['3A','3B','4A','4B','5A','5B','6A','6B','7A','7B']
alumnos = []
dni_counter = 44000001

for ci, curso in enumerate(cursos):
    for j in range(20):
        if j < 10:
            nombre  = nombres_m[j]
            sufijo  = 'm'
        else:
            nombre  = nombres_v[j - 10]
            sufijo  = 'f'
        apellido = apellidos[j % len(apellidos)]
        dni = str(dni_counter)
        dni_counter += 7  # evitar colisiones
        username = f"alu_{curso.lower()}_{j+1:02d}"
        email    = f"{username}@proa.edu.ar"
        a, _ = Alumno.objects.get_or_create(dni=dni, defaults={
            'nombre': nombre, 'apellido': apellido,
            'curso': curso, 'email': email,
        })
        alumnos.append(a)

# Alumno inactivo en 4A para demo reactivar/eliminar
alu_inactivo, _ = Alumno.objects.get_or_create(dni='99000001', defaults={
    'nombre': 'Pedro', 'apellido': 'Inactivo', 'curso': '4A',
    'email': 'pinactivo@proa.edu.ar', 'activo': False,
})
if alu_inactivo.activo:
    alu_inactivo.activo = False
    alu_inactivo.save()

print(f"✅ {len(alumnos)} alumnos + 1 inactivo para demo")


# ══════════════════════════════════════════════════════════════════
#  CATEGORÍAS
# ══════════════════════════════════════════════════════════════════
cats = {}
for nombre, color in [
    ('Electrónica',       '#2E86DE'),
    ('Mecánica',          '#27AE60'),
    ('Madera',            '#E67E22'),
    ('Metalmecánica',     '#C0392B'),
    ('Construcción',      '#8E44AD'),
    ('Medición',          '#16A085'),
    ('Soldadura',         '#D35400'),
    ('Máquinas Fijas',    '#2C3E50'),
    ('Herramientas Mano', '#7F8C8D'),
]:
    c, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={'color_hex': color})
    cats[nombre] = c
print(f"✅ {len(cats)} categorías")


# ══════════════════════════════════════════════════════════════════
#  HERRAMIENTAS
# ══════════════════════════════════════════════════════════════════
def h_get_or_create(nombre, cat, ubi, estado, marca='', modelo='', tipo='HERRAMIENTA', fecha=date(2023,3,1)):
    obj, _ = Herramienta.objects.get_or_create(nombre=nombre, defaults={
        'categoria': cats.get(cat), 'ubicacion': ubi, 'estado': estado,
        'marca': marca, 'modelo': modelo, 'tipo': tipo,
        'fecha_compra': fecha, 'activo': estado != 'BAJA',
    })
    return obj

# ── HERRAMIENTAS DE MANO ─────────────────────────────────────────
mano_data = [
    # (nombre,                           categoría,          ubicación,    estado)
    ('Martillo de bola 500g #1',         'Herramientas Mano','Estante A-1','DISPONIBLE'),
    ('Martillo de bola 500g #2',         'Herramientas Mano','Estante A-1','DISPONIBLE'),
    ('Martillo de bola 500g #3',         'Herramientas Mano','Estante A-1','PRESTADA'),
    ('Martillo de goma #1',              'Herramientas Mano','Estante A-1','DISPONIBLE'),
    ('Martillo de goma #2',              'Herramientas Mano','Estante A-1','DISPONIBLE'),
    ('Destornilladores planos jgo #1',   'Herramientas Mano','Cajón A-1',  'DISPONIBLE'),
    ('Destornilladores planos jgo #2',   'Herramientas Mano','Cajón A-1',  'DISPONIBLE'),
    ('Destornilladores planos jgo #3',   'Herramientas Mano','Cajón A-1',  'PRESTADA'),
    ('Destornilladores Phillips jgo #1', 'Herramientas Mano','Cajón A-1',  'DISPONIBLE'),
    ('Destornilladores Phillips jgo #2', 'Herramientas Mano','Cajón A-1',  'DISPONIBLE'),
    ('Destornilladores Phillips jgo #3', 'Herramientas Mano','Cajón A-1',  'DISPONIBLE'),
    ('Destornilladores Torx jgo #1',     'Herramientas Mano','Cajón A-2',  'DISPONIBLE'),
    ('Llave inglesa 10" #1',             'Herramientas Mano','Cajón B-1',  'DISPONIBLE'),
    ('Llave inglesa 10" #2',             'Herramientas Mano','Cajón B-1',  'DISPONIBLE'),
    ('Llave inglesa 12" #1',             'Herramientas Mano','Cajón B-1',  'DISPONIBLE'),
    ('Llave inglesa 12" #2',             'Herramientas Mano','Cajón B-1',  'PRESTADA'),
    ('Llaves combinadas jgo métrico #1', 'Herramientas Mano','Cajón B-2',  'DISPONIBLE'),
    ('Llaves combinadas jgo métrico #2', 'Herramientas Mano','Cajón B-2',  'DISPONIBLE'),
    ('Llaves combinadas jgo métrico #3', 'Herramientas Mano','Cajón B-2',  'DISPONIBLE'),
    ('Llaves Allen jgo métrico #1',      'Herramientas Mano','Cajón B-3',  'DISPONIBLE'),
    ('Llaves Allen jgo métrico #2',      'Herramientas Mano','Cajón B-3',  'DISPONIBLE'),
    ('Llaves Allen jgo pulgadas #1',     'Herramientas Mano','Cajón B-3',  'DISPONIBLE'),
    ('Alicates universales #1',          'Herramientas Mano','Cajón C-1',  'DISPONIBLE'),
    ('Alicates universales #2',          'Herramientas Mano','Cajón C-1',  'DISPONIBLE'),
    ('Alicates universales #3',          'Herramientas Mano','Cajón C-1',  'PRESTADA'),
    ('Alicates de punta #1',             'Herramientas Mano','Cajón C-1',  'DISPONIBLE'),
    ('Alicates de punta #2',             'Herramientas Mano','Cajón C-1',  'DISPONIBLE'),
    ('Alicates de corte #1',             'Herramientas Mano','Cajón C-2',  'DISPONIBLE'),
    ('Alicates de corte #2',             'Herramientas Mano','Cajón C-2',  'DISPONIBLE'),
    ('Alicates de presión #1',           'Herramientas Mano','Cajón C-2',  'DISPONIBLE'),
    ('Alicates de presión #2',           'Herramientas Mano','Cajón C-2',  'REPARACION'),
    ('Pinza amperimétrica #1',           'Medición',         'Estante A-3','DISPONIBLE'),
    ('Pinza amperimétrica #2',           'Medición',         'Estante A-3','DISPONIBLE'),
    ('Pinza amperimétrica #3',           'Medición',         'Estante A-3','PRESTADA'),
    ('Multímetro digital #1',            'Medición',         'Estante A-3','DISPONIBLE'),
    ('Multímetro digital #2',            'Medición',         'Estante A-3','DISPONIBLE'),
    ('Multímetro digital #3',            'Medición',         'Estante A-3','DISPONIBLE'),
    ('Multímetro digital #4',            'Medición',         'Estante A-3','PRESTADA'),
    ('Multímetro digital #5',            'Medición',         'Estante A-3','DISPONIBLE'),
    ('Calibre Vernier 150mm #1',         'Medición',         'Estante A-4','DISPONIBLE'),
    ('Calibre Vernier 150mm #2',         'Medición',         'Estante A-4','DISPONIBLE'),
    ('Calibre Vernier 150mm #3',         'Medición',         'Estante A-4','PRESTADA'),
    ('Micrómetro externo 0-25mm',        'Medición',         'Estante A-4','DISPONIBLE'),
    ('Micrómetro externo 25-50mm',       'Medición',         'Estante A-4','DISPONIBLE'),
    ('Escuadra metálica 300mm #1',       'Medición',         'Cajón D-1',  'DISPONIBLE'),
    ('Escuadra metálica 300mm #2',       'Medición',         'Cajón D-1',  'DISPONIBLE'),
    ('Nivel de burbuja 60cm #1',         'Medición',         'Cajón D-1',  'DISPONIBLE'),
    ('Nivel de burbuja 60cm #2',         'Medición',         'Cajón D-1',  'DISPONIBLE'),
    ('Flexómetro 5m #1',                 'Medición',         'Cajón D-2',  'DISPONIBLE'),
    ('Flexómetro 5m #2',                 'Medición',         'Cajón D-2',  'DISPONIBLE'),
    ('Flexómetro 5m #3',                 'Medición',         'Cajón D-2',  'DISPONIBLE'),
    ('Flexómetro 5m #4',                 'Medición',         'Cajón D-2',  'DISPONIBLE'),
    ('Arco de sierra #1',                'Herramientas Mano','Estante B-1','DISPONIBLE'),
    ('Arco de sierra #2',                'Herramientas Mano','Estante B-1','DISPONIBLE'),
    ('Arco de sierra #3',                'Herramientas Mano','Estante B-1','DISPONIBLE'),
    ('Serrucho carpintero #1',           'Madera',           'Estante B-1','DISPONIBLE'),
    ('Serrucho carpintero #2',           'Madera',           'Estante B-1','DISPONIBLE'),
    ('Limas planas bastarda jgo #1',     'Herramientas Mano','Cajón E-1',  'DISPONIBLE'),
    ('Limas planas bastarda jgo #2',     'Herramientas Mano','Cajón E-1',  'DISPONIBLE'),
    ('Limas redondas jgo #1',            'Herramientas Mano','Cajón E-1',  'DISPONIBLE'),
    ('Punzones jgo #1',                  'Herramientas Mano','Cajón E-2',  'DISPONIBLE'),
    ('Punzones jgo #2',                  'Herramientas Mano','Cajón E-2',  'DISPONIBLE'),
    ('Cincel plano #1',                  'Herramientas Mano','Cajón E-2',  'DISPONIBLE'),
    ('Cincel plano #2',                  'Herramientas Mano','Cajón E-2',  'DISPONIBLE'),
    ('Remachadora manual #1',            'Mecánica',         'Cajón F-1',  'DISPONIBLE'),
    ('Remachadora manual #2',            'Mecánica',         'Cajón F-1',  'DISPONIBLE'),
    ('Pistola de silicona #1',           'Construcción',     'Cajón F-1',  'DISPONIBLE'),
    ('Pistola de silicona #2',           'Construcción',     'Cajón F-1',  'DISPONIBLE'),
    ('Pistola de silicona #3',           'Construcción',     'Cajón F-1',  'DISPONIBLE'),
]
herr_mano = []
for row in mano_data:
    h = h_get_or_create(row[0], row[1], row[2], row[3])
    herr_mano.append(h)

# ── HERRAMIENTAS PORTÁTILES (eléctricas) ────────────────────────
portatiles_data = [
    ('Perforadora rotopercutora #1',  'Mecánica','Estante B-2','DISPONIBLE','Bosch',        'GSB 18V-110C'),
    ('Perforadora rotopercutora #2',  'Mecánica','Estante B-2','DISPONIBLE','Bosch',        'GSB 18V-110C'),
    ('Perforadora rotopercutora #3',  'Mecánica','Estante B-2','PRESTADA',  'Bosch',        'GSB 18V-110C'),
    ('Taladro inalámbrico #1',        'Mecánica','Estante B-2','DISPONIBLE','DeWalt',       'DCD776'),
    ('Taladro inalámbrico #2',        'Mecánica','Estante B-2','DISPONIBLE','DeWalt',       'DCD776'),
    ('Taladro inalámbrico #3',        'Mecánica','Estante B-2','PRESTADA',  'DeWalt',       'DCD776'),
    ('Sierra circular #1',            'Madera',  'Estante C-1','DISPONIBLE','Skil',         'HD5867'),
    ('Sierra circular #2',            'Madera',  'Estante C-1','DISPONIBLE','Skil',         'HD5867'),
    ('Caladora #1',                   'Madera',  'Estante C-1','DISPONIBLE','Black&Decker', 'KS701PE'),
    ('Caladora #2',                   'Madera',  'Estante C-1','DISPONIBLE','Black&Decker', 'KS701PE'),
    ('Caladora #3',                   'Madera',  'Estante C-1','REPARACION','Black&Decker', 'KS701PE'),
    ('Fresadora portátil #1',         'Madera',  'Estante C-2','DISPONIBLE','Makita',       'RP0900'),
    ('Amoladora angular 4.5" #1',     'Metalmecánica','Estante B-3','DISPONIBLE','DeWalt',  'DWE402'),
    ('Amoladora angular 4.5" #2',     'Metalmecánica','Estante B-3','DISPONIBLE','DeWalt',  'DWE402'),
    ('Amoladora angular 4.5" #3',     'Metalmecánica','Estante B-3','PRESTADA',  'DeWalt',  'DWE402'),
    ('Amoladora angular 4.5" #4',     'Metalmecánica','Estante B-3','DISPONIBLE','Bosch',   'GWS 1400'),
]
herr_port = []
for row in portatiles_data:
    h = h_get_or_create(*row)
    herr_port.append(h)

# ── MÁQUINAS (tipo=MAQUINA) ──────────────────────────────────────
maquinas_data = [
    # Soldadoras MMA/Electrodo (×3)
    ('Soldadora MMA Electrodo #1','Soldadura','Zona Soldadura','DISPONIBLE','Lincoln Electric','Invertec V155-S','MAQUINA'),
    ('Soldadora MMA Electrodo #2','Soldadura','Zona Soldadura','DISPONIBLE','Lincoln Electric','Invertec V155-S','MAQUINA'),
    ('Soldadora MMA Electrodo #3','Soldadura','Zona Soldadura','PRESTADA',  'Miller',          'Diversion 165','MAQUINA'),
    # Soldadoras MIG (×2)
    ('Soldadora MIG #1',         'Soldadura','Zona Soldadura','DISPONIBLE','Lincoln Electric','Easy MIG 180','MAQUINA'),
    ('Soldadora MIG #2',         'Soldadura','Zona Soldadura','REPARACION','Miller',          'Millermatic 211','MAQUINA'),
    # Soldadora TIG (×1)
    ('Soldadora TIG #1',         'Soldadura','Zona Soldadura','DISPONIBLE','Lincoln Electric','Square Wave TIG 200','MAQUINA'),
    # Tornos
    ('Torno para metales #1',    'Máquinas Fijas','Zona Tornos','DISPONIBLE','Romi',   'C 420','MAQUINA'),
    ('Torno para madera #1',     'Máquinas Fijas','Zona Tornos','DISPONIBLE','Tornado','TW-1000','MAQUINA'),
    ('Torno para madera #2',     'Máquinas Fijas','Zona Tornos','DISPONIBLE','Tornado','TW-1000','MAQUINA'),
    ('Torno para madera #3',     'Máquinas Fijas','Zona Tornos','REPARACION','Tornado','TW-750','MAQUINA'),
    # Fresadora CNC
    ('Fresadora CNC #1',         'Máquinas Fijas','Zona CNC',  'DISPONIBLE','Leadshine','MX3660','MAQUINA'),
    # Perforadoras de banco
    ('Perforadora de banco #1',  'Mecánica',      'Zona Bancos','DISPONIBLE','Gamma','G19010AR','MAQUINA'),
    ('Perforadora de banco #2',  'Mecánica',      'Zona Bancos','DISPONIBLE','Gamma','G19010AR','MAQUINA'),
]
maquinas = []
for row in maquinas_data:
    nombre, cat, ubi, estado, marca, modelo, tipo = row
    h = h_get_or_create(nombre, cat, ubi, estado, marca, modelo, tipo, date(2022,6,1))
    maquinas.append(h)

total_herr = len(herr_mano) + len(herr_port) + len(maquinas)
print(f"✅ {total_herr} herramientas/máquinas ({len(herr_mano)} mano, {len(herr_port)} portátiles, {len(maquinas)} máquinas fijas)")


# ══════════════════════════════════════════════════════════════════
#  INSUMOS (20)
# ══════════════════════════════════════════════════════════════════
insumos_data = [
    # (nombre,                              categoría,       unidad,    stock_actual, stock_min)
    ('Electrodos E6013 2.5mm',              'Soldadura',     'unidades', 80,   50),
    ('Electrodos E6013 3.2mm',              'Soldadura',     'unidades', 35,   50),   # CRÍTICO
    ('Electrodos E7018 3.2mm',              'Soldadura',     'unidades', 60,   30),
    ('Alambre MIG 0.8mm (rollo 5kg)',       'Soldadura',     'unidades',  3,    2),
    ('Alambre MIG 1.0mm (rollo 5kg)',       'Soldadura',     'unidades',  1,    2),   # CRÍTICO
    ('Gas argón mezcla 75/25 (m³)',         'Soldadura',     'litros',    8,    5),
    ('Pintura antióxido gris (lata 1L)',    'Metalmecánica', 'unidades',  4,    3),
    ('Pintura esmalte negro (lata 1L)',     'Metalmecánica', 'unidades',  2,    3),   # CRÍTICO
    ('Aceite de corte (litro)',             'Mecánica',      'litros',    5,    3),
    ('Lubricante WD-40 (aerosol)',          'Mecánica',      'unidades',  6,    4),
    ('Discos de corte 4.5" (pack 5)',       'Metalmecánica', 'unidades', 12,    8),
    ('Discos de desbaste 4.5" (pack 5)',    'Metalmecánica', 'unidades',  4,    6),   # CRÍTICO
    ('Lija grano 80 (hoja)',               'Madera',        'hojas',    30,   20),
    ('Lija grano 120 (hoja)',              'Madera',        'hojas',    25,   20),
    ('Lija grano 220 (hoja)',              'Madera',        'hojas',     8,   15),   # CRÍTICO
    ('Brocas HSS 6mm (juego 10u)',         'Mecánica',      'unidades',  5,    4),
    ('Brocas HSS 8mm (juego 10u)',         'Mecánica',      'unidades',  3,    4),   # CRÍTICO
    ('Clavos 2" (caja 1kg)',               'Madera',        'unidades',  8,    3),
    ('Tornillos autorroscantes jgo',       'Construcción',  'unidades', 12,    5),
    ('Tuercas/Bulones surtido',            'Mecánica',      'unidades', 15,    5),
]
insumos = []
for nombre, cat, unidad, stock_actual, stock_minimo in insumos_data:
    ins, _ = Insumo.objects.get_or_create(nombre=nombre, defaults={
        'categoria': cats.get(cat), 'unidad': unidad,
        'stock_actual': stock_actual, 'stock_minimo': stock_minimo,
    })
    insumos.append(ins)
print(f"✅ {len(insumos)} insumos (6 en stock crítico para demo alertas)")


# ══════════════════════════════════════════════════════════════════
#  MOVIMIENTOS DE INSUMOS (historial)
# ══════════════════════════════════════════════════════════════════
def mov(insumo, tipo, cantidad, obs):
    MovimientoInsumo.objects.create(
        insumo=insumo, tipo=tipo, cantidad=cantidad, observacion=obs
    )

# Algunos movimientos históricos para que el historial no quede vacío
mov(insumos[0], 'ENTRADA',  200, 'Compra inicial – licitación 2026')
mov(insumos[0], 'ENTREGA',   30, 'Prácticas soldadura 3A – marzo')
mov(insumos[0], 'ENTREGA',   50, 'Prácticas soldadura 4B – abril')
mov(insumos[0], 'ENTREGA',   40, 'Prácticas soldadura 5A – mayo')
mov(insumos[2], 'ENTRADA',  100, 'Compra inicial')
mov(insumos[2], 'ENTREGA',   40, 'Prácticas 4A – abril')
mov(insumos[9], 'ENTRADA',   12, 'Compra inicial')
mov(insumos[9], 'ENTREGA',    6, 'Uso taller general')
mov(insumos[12],'ENTRADA',   60, 'Compra inicial')
mov(insumos[12],'ENTREGA',   30, 'Prácticas madera 3B')
print("✅ Movimientos de insumos históricos")


# ══════════════════════════════════════════════════════════════════
#  PRÉSTAMOS (12 en distintos estados)
# ══════════════════════════════════════════════════════════════════
# Referencia rápida de herramientas con estado correcto
h_disp  = lambda nombre: Herramienta.objects.filter(nombre__icontains=nombre, estado='DISPONIBLE').first()

alu = {curso: Alumno.objects.filter(curso=curso, activo=True).first() for curso in cursos}
doc = docentes[0]
doc2 = docentes[1]
doc3 = docentes[2]

# 1. Préstamo activo, no vencido
h1 = Herramienta.objects.filter(nombre='Multímetro digital #1').first()
if h1 and h1.estado == 'DISPONIBLE':
    p, created = Prestamo.objects.get_or_create(
        alumno=alu['3A'], herramienta=h1, fecha_devolucion__isnull=True,
        defaults={
            'docente': doc,
            'fecha_prestamo': timezone.now() - timedelta(hours=4),
            'modulo_clase': 'Módulo Electrónica – Medición'
        }
    )
    if created:
        h1.estado = 'PRESTADA'; h1.save()

# 2. Préstamo activo, no vencido – máquina
h2 = Herramienta.objects.filter(nombre='Soldadora MMA Electrodo #3').first()
if h2:
    p2, created = Prestamo.objects.get_or_create(
        alumno=alu['5A'], herramienta=h2, fecha_devolucion__isnull=True,
        defaults={
            'docente': doc2,
            'fecha_prestamo': timezone.now() - timedelta(hours=2),
            'modulo_clase': 'Módulo Soldadura – Electrodo'
        }
    )

# 3. Préstamo VENCIDO (>2 días) – para demo de alerta
h3 = Herramienta.objects.filter(nombre='Alicates universales #3').first()
if h3:
    p3, created = Prestamo.objects.get_or_create(
        alumno=alu['4A'], herramienta=h3, fecha_devolucion__isnull=True,
        defaults={
            'docente': doc,
            'fecha_prestamo': timezone.now() - timedelta(days=4),
            'notificado_vencimiento': False,
        }
    )

# 4. Préstamo VENCIDO (>2 días) – ya notificado
h4 = Herramienta.objects.filter(nombre='Calibre Vernier 150mm #3').first()
if h4:
    p4, created = Prestamo.objects.get_or_create(
        alumno=alu['6A'], herramienta=h4, fecha_devolucion__isnull=True,
        defaults={
            'docente': doc3,
            'fecha_prestamo': timezone.now() - timedelta(days=3),
            'notificado_vencimiento': True,
        }
    )

# 5. Préstamo ACTIVO – amoladora
h5 = Herramienta.objects.filter(nombre='Amoladora angular 4.5" #3').first()
if h5:
    p5, created = Prestamo.objects.get_or_create(
        alumno=alu['7A'], herramienta=h5, fecha_devolucion__isnull=True,
        defaults={'docente': doc2, 'fecha_prestamo': timezone.now() - timedelta(hours=1)}
    )

# 6. Préstamo DEVUELTO – buen estado
h6 = Herramienta.objects.filter(nombre='Perforadora rotopercutora #3').first()
if h6:
    alu_3b = Alumno.objects.filter(curso='3B', activo=True).first()
    p6, created = Prestamo.objects.get_or_create(
        alumno=alu_3b, herramienta=h6, fecha_devolucion__isnull=False,
        defaults={
            'docente': doc,
            'fecha_prestamo': timezone.now() - timedelta(days=1, hours=3),
            'fecha_devolucion': timezone.now() - timedelta(hours=2),
            'estado_devolucion': 'BUEN_ESTADO',
            'observaciones': 'Devuelta en perfectas condiciones.',
        }
    )

# 7. Préstamo DEVUELTO – desgaste leve
h7 = Herramienta.objects.filter(nombre='Taladro inalámbrico #3').first()
if h7:
    alu_4b = Alumno.objects.filter(curso='4B', activo=True).first()
    p7, created = Prestamo.objects.get_or_create(
        alumno=alu_4b, herramienta=h7, fecha_devolucion__isnull=False,
        defaults={
            'docente': doc2,
            'fecha_prestamo': timezone.now() - timedelta(days=2),
            'fecha_devolucion': timezone.now() - timedelta(days=1),
            'estado_devolucion': 'DESGASTE',
            'observaciones': 'Chuck con leve desgaste en la mordaza.',
        }
    )

# 8. Préstamo DEVUELTO – requiere reparación (→ herramienta en REPARACION)
h8 = Herramienta.objects.filter(nombre='Caladora #3').first()
if h8:
    alu_5b = Alumno.objects.filter(curso='5B', activo=True).first()
    p8, created = Prestamo.objects.get_or_create(
        alumno=alu_5b, herramienta=h8, fecha_devolucion__isnull=False,
        defaults={
            'docente': doc3,
            'fecha_prestamo': timezone.now() - timedelta(days=3),
            'fecha_devolucion': timezone.now() - timedelta(days=2),
            'estado_devolucion': 'REPARACION',
            'observaciones': 'Se rompió la hoja guía. Necesita repuesto.',
        }
    )

# 9-12. Préstamos devueltos adicionales para historial
extras = [
    ('Martillo de bola 500g #3', '3A', doc,  'BUEN_ESTADO', 5, 2),
    ('Llave inglesa 12" #2',     '4A', doc2, 'BUEN_ESTADO', 4, 1),
    ('Pinza amperimétrica #3',   '5A', doc,  'DESGASTE',    3, 1),
    ('Multímetro digital #4',    '6B', doc3, 'BUEN_ESTADO', 6, 3),
]
for nombre_h, curso_a, docente_e, estado_dev, dias_p, dias_d in extras:
    hx = Herramienta.objects.filter(nombre=nombre_h).first()
    ax = Alumno.objects.filter(curso=curso_a, activo=True).first()
    if hx and ax:
        Prestamo.objects.get_or_create(
            alumno=ax, herramienta=hx,
            fecha_prestamo__date=(timezone.now() - timedelta(days=dias_p)).date(),
            defaults={
                'docente': docente_e,
                'fecha_prestamo': timezone.now() - timedelta(days=dias_p),
                'fecha_devolucion': timezone.now() - timedelta(days=dias_d),
                'estado_devolucion': estado_dev,
            }
        )

print("✅ 12 préstamos (activos, vencidos, devueltos en distintos estados)")


# ══════════════════════════════════════════════════════════════════
#  PLANES DE MANTENIMIENTO (10 casos de uso)
# ══════════════════════════════════════════════════════════════════
def plan(nombre, herramienta_nombre, tipo, desc, frec, prox, tareas=None):
    h = Herramienta.objects.filter(nombre=herramienta_nombre).first()
    if not h:
        return None
    p, _ = PlanMantenimiento.objects.get_or_create(nombre=nombre, defaults={
        'herramienta': h, 'tipo': tipo, 'descripcion': desc,
        'frecuencia_dias': frec, 'proxima_ejecucion': prox, 'activo': True,
    })
    if tareas:
        for orden, (tdesc, resp, dur) in enumerate(tareas, 1):
            TareaMantenimiento.objects.get_or_create(plan=p, descripcion=tdesc,
                defaults={'responsable': resp, 'duracion_estimada_min': dur, 'orden': orden})
    return p

# 1. PREVENTIVO VENCIDO (>7 días) — debería aparecer en rojo
p1 = plan(
    'Mantenimiento mensual – Torno metales #1',
    'Torno para metales #1', 'PREV',
    'Limpieza de virutas, lubricación de carros y revisión eléctrica.',
    30, date.today() - timedelta(days=12),
    tareas=[
        ('Limpiar viruta de carros y bancada',   'Pañolero',          15),
        ('Lubricar carros transversal y axial',  'Pañolero',          10),
        ('Revisar tensión de correa y poleas',   'Docente de taller', 10),
        ('Verificar sistema eléctrico y freno',  'Docente de taller', 15),
        ('Prueba de giro en vacío',              'Docente de taller',  5),
    ]
)

# 2. PREVENTIVO VENCIDO — compresor
p2 = plan(
    'Mantenimiento mensual – Perforadora banco #1',
    'Perforadora de banco #1', 'PREV',
    'Limpieza de filtro, lubricación de columna y verificación de mordaza.',
    30, date.today() - timedelta(days=9),
    tareas=[
        ('Limpiar filtro de aire',              'Pañolero',  10),
        ('Lubricar columna y husillo',           'Pañolero',   5),
        ('Verificar mordaza y mesa',             'Pañolero',   5),
        ('Probar seguro de encendido',           'Pañolero',   5),
    ]
)

# 3. PREVENTIVO PRÓXIMO (dentro de 7 días)
p3 = plan(
    'Mantenimiento trimestral – Soldadora TIG',
    'Soldadora TIG #1', 'PREV',
    'Limpieza de tobera, revisión de antorcha, calibración de amperaje.',
    90, date.today() + timedelta(days=4),
    tareas=[
        ('Limpiar tobera y difusor de gas',     'Técnico externo',   20),
        ('Revisar cable y antorcha',             'Técnico externo',   15),
        ('Calibrar amperaje de referencia',      'Docente de taller', 10),
        ('Verificar caudal de gas argón',        'Pañolero',          10),
    ]
)

# 4. PREVENTIVO PRÓXIMO — Fresadora CNC
p4 = plan(
    'Mantenimiento semanal – Fresadora CNC',
    'Fresadora CNC #1', 'PREV',
    'Limpieza de mesa, lubricación de ejes y verificación de firmware.',
    7, date.today() + timedelta(days=6),
    tareas=[
        ('Limpiar mesa y canales en T',          'Pañolero',          10),
        ('Lubricar ejes X, Y, Z',                'Pañolero',           5),
        ('Verificar posición de origen',         'Docente de taller',  5),
    ]
)

# 5. PREVENTIVO AL DÍA (en más de 7 días)
p5 = plan(
    'Mantenimiento trimestral – Torno madera #1',
    'Torno para madera #1', 'PREV',
    'Revisión de cabezal, ajuste de correa y lubricación de bancada.',
    90, date.today() + timedelta(days=45),
    tareas=[
        ('Revisar y ajustar correa de transmisión', 'Pañolero',        10),
        ('Lubricar bancada y portaherramientas',    'Pañolero',        10),
        ('Verificar concentricidad del plato',      'Docente de taller',10),
    ]
)

# 6. PREVENTIVO AL DÍA — soldadora MIG
p6 = plan(
    'Mantenimiento semestral – Soldadora MIG #1',
    'Soldadora MIG #1', 'PREV',
    'Revisión completa de conexiones, rodillos de arrastre y tobera.',
    180, date.today() + timedelta(days=60)
)

# 7. CORRECTIVO PENDIENTE — Soldadora MIG #2 (en reparación)
p7 = plan(
    'Reparación – Soldadora MIG #2 (rodillo de arrastre)',
    'Soldadora MIG #2', 'CORR',
    'Reemplazo de rodillo de arrastre de alambre roto. Revisión de PCB.',
    None, date.today() + timedelta(days=3),
    tareas=[
        ('Desmontar panel lateral',              'Técnico externo',   20),
        ('Reemplazar rodillo de arrastre',       'Técnico externo',   30),
        ('Verificar PCB de control',             'Técnico externo',   20),
        ('Prueba de arco de soldadura',          'Docente de taller', 15),
    ]
)

# 8. CORRECTIVO PENDIENTE — Caladora #3
p8 = plan(
    'Reparación – Caladora #3 (hoja guía)',
    'Caladora #3', 'CORR',
    'Reemplazo de hoja guía rota y revisión de sistema de sujeción.',
    None, date.today() + timedelta(days=2),
    tareas=[
        ('Comprar repuesto hoja guía',           'Pañolero',          10),
        ('Reemplazar hoja guía',                 'Docente de taller', 20),
        ('Probar sujeción y vibración',          'Docente de taller', 10),
    ]
)

# 9. CORRECTIVO PENDIENTE — Torno madera #3
p9 = plan(
    'Reparación – Torno madera #3 (correa)',
    'Torno para madera #3', 'CORR',
    'Reemplazo de correa de transmisión rota.',
    None, date.today() + timedelta(days=5),
    tareas=[
        ('Adquirir correa de repuesto',          'Pañolero',          15),
        ('Desmontar protección y poleas',        'Técnico externo',   30),
        ('Instalar correa nueva',                'Técnico externo',   20),
        ('Prueba de funcionamiento',             'Docente de taller',  5),
    ]
)

# 10. PREVENTIVO VENCIDO — Perforadora banco #2 (sin tareas — caso simple)
p10 = plan(
    'Limpieza semestral – Perforadora banco #2',
    'Perforadora de banco #2', 'PREV',
    'Limpieza general y lubricación básica.',
    180, date.today() - timedelta(days=20)
)

print("✅ 10 planes de mantenimiento (3 vencidos, 2 próximos, 2 al día, 3 correctivos)")


# ══════════════════════════════════════════════════════════════════
#  EJECUCIÓN DE MANTENIMIENTO (historial de un plan ejecutado)
# ══════════════════════════════════════════════════════════════════
# Simular que el plan de Perforadora de banco #1 fue ejecutado la vez anterior
if p2:
    plan_anterior, _ = PlanMantenimiento.objects.get_or_create(
        nombre='Mantenimiento mensual – Perforadora banco #1 (ejecución anterior)',
        defaults={
            'herramienta': p2.herramienta,
            'tipo': 'PREV',
            'descripcion': p2.descripcion,
            'frecuencia_dias': 30,
            'proxima_ejecucion': date.today() - timedelta(days=9),
            'activo': False,
        }
    )
    ej, _ = EjecucionMantenimiento.objects.get_or_create(
        plan=plan_anterior,
        fecha=date.today() - timedelta(days=39),
        defaults={
            'realizado_por': 'Roberto García',
            'es_externo': False,
            'costo': 0,
            'notas': 'Mantenimiento preventivo realizado sin novedades.',
        }
    )
print("✅ Ejecución de mantenimiento histórica registrada")


# ══════════════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════
from core.models import Alumno as A, Herramienta as H, Prestamo as P
print()
print("═" * 60)
print("🎉 SEED DE PRESENTACIÓN CARGADO CORRECTAMENTE")
print("═" * 60)
print()
print("USUARIOS:")
print("  admin       / admin123      → Administrador")
print("  panolero1   / panolero123   → Pañolero")
print("  panolero2   / panolero123   → Pañolero")
print("  martinez    / docente123    → Docente")
print("  alumno1     / alumno123     → Alumno")
print()
print(f"ALUMNOS:       {A.objects.filter(activo=True).count()} activos + 1 inactivo (demo reactivar)")
print(f"DOCENTES:      {Docente.objects.count()}")
print(f"HERRAMIENTAS:  {H.objects.filter(activo=True).count()} activas")
print(f"  Disponibles: {H.objects.filter(estado='DISPONIBLE').count()}")
print(f"  Prestadas:   {H.objects.filter(estado='PRESTADA').count()}")
print(f"  Reparación:  {H.objects.filter(estado='REPARACION').count()}")
print(f"PRÉSTAMOS:")
print(f"  Activos:     {P.objects.filter(fecha_devolucion__isnull=True).count()}")
print(f"  Devueltos:   {P.objects.filter(fecha_devolucion__isnull=False).count()}")
print(f"INSUMOS CRÍTICOS: {sum(1 for i in Insumo.objects.filter(activo=True) if i.es_critico)}")
print()
