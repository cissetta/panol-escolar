# 🔧 Sistema de Gestión de Pañol Escolar
## PROA Villa del Totoral – Programación IV 2026

---

## Descripción

Sistema web desarrollado con **Django 4.2** para gestionar herramientas, insumos, préstamos y mantenimiento del pañol escolar de la PROA.

El proyecto base incluye:
- ✅ Autenticación completa (login / logout / perfil)
- ✅ Sistema de roles (Admin, Pañolero, Docente, Alumno)
- ✅ Modelos de datos centrales (`core/models.py`)
- ✅ Dashboard con indicadores en tiempo real
- ✅ Estructura de apps por módulo (una por grupo)
- ✅ Admin de Django configurado
- ✅ Datos de prueba (seed)

---

## Requisitos previos

- Python 3.10 o superior
- Git
- pip

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU-USUARIO/panol-escolar.git
cd panol-escolar
```

### 2. Crear y activar el entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Cargar datos de prueba

```bash
python manage.py shell < seed.py
```

Esto crea los siguientes usuarios de prueba:

| Usuario     | Contraseña    | Rol       |
|-------------|---------------|-----------|
| `admin`     | `admin123`    | Admin     |
| `panolero`  | `panolero123` | Pañolero  |
| `martinez`  | `docente123`  | Docente   |
| `lopez`     | `docente123`  | Docente   |
| `gonzalez`  | `alumno123`   | Alumno    |

También crea: 8 alumnos, 20 herramientas, 10 insumos, 3 préstamos activos, 4 planes de mantenimiento.

### 6. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrí el navegador en: **http://127.0.0.1:8000/**

---

## Estructura del proyecto

```
panol-escolar/
├── manage.py
├── requirements.txt
├── seed.py                     # Script de datos de prueba
│
├── panol_escolar/              # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                   # Login, roles, perfiles (IMPLEMENTADO)
│   ├── models.py               # Modelo Perfil
│   ├── views.py                # login / logout / perfil
│   ├── decorators.py           # @solo_admin, @solo_panolero, etc.
│   └── templates/accounts/
│       └── login.html
│
├── core/                       # Dashboard + modelos centrales (IMPLEMENTADO)
│   ├── models.py               # ⭐ TODOS los modelos del sistema
│   ├── views.py                # Dashboard
│   └── templates/
│       ├── base.html           # Template base con sidebar
│       └── core/dashboard.html
│
├── alumnos/                    # GRUPO 1 – Para implementar
├── inventario/                 # GRUPO 2 – Para implementar
├── prestamos/                  # GRUPO 3 – Para implementar
├── mantenimiento/              # GRUPO 4 – Para implementar
└── reportes/                   # GRUPO 5 – Para implementar
```

---

## Flujo de trabajo Git (obligatorio)

### Ramas del proyecto

```
main          → producción (solo el profesor puede mergear)
develop       → integración (todos trabajan aquí)
feature/G1-*  → features del Grupo 1
feature/G2-*  → features del Grupo 2
...
```

### Ciclo de trabajo diario

```bash
# 1. Antes de empezar: actualizar develop
git checkout develop
git pull origin develop

# 2. Crear tu rama de feature
git checkout -b feature/G1-lista-alumnos

# 3. Trabajar, commitear frecuentemente
git add .
git commit -m "feat(alumnos): agrega vista de lista con paginación"

# 4. Subir tu rama
git push origin feature/G1-lista-alumnos

# 5. Abrir Pull Request hacia develop en GitHub
```

### Convención de commits

```
feat(módulo): descripción corta      → nueva funcionalidad
fix(módulo): descripción corta       → corrección de bug
style(módulo): descripción corta     → cambios de estilo/CSS
test(módulo): descripción corta      → tests
docs(módulo): descripción corta      → documentación
```

---

## Cómo usar los decoradores de rol

```python
from accounts.decorators import solo_panolero, solo_docente

@login_required
@solo_panolero
def mi_vista(request):
    ...
```

Roles disponibles: `ADMIN`, `PANOLERO`, `DOCENTE`, `ALUMNO`

---

## Cómo acceder a los modelos desde cualquier app

Los modelos están en `core/models.py`. Para usarlos en otras apps:

```python
from core.models import Alumno, Herramienta, Prestamo, Insumo
```

---

## Asignación de módulos por grupo

| Grupo | App          | Módulo                         |
|-------|--------------|--------------------------------|
| G1    | `alumnos/`   | ABM de alumnos + QR            |
| G2    | `inventario/`| Herramientas + Insumos         |
| G3    | `prestamos/` | Préstamos y devoluciones       |
| G4    | `mantenimiento/` | Planes y hoja de vida      |
| G5    | `reportes/`  | Reportes + Configuración       |

---

## Ejecutar tests

```bash
python manage.py test
```

Para correr tests de un módulo específico:

```bash
python manage.py test alumnos
python manage.py test inventario
```

---

## Variables de entorno (producción)

En producción, crear un archivo `.env` en la raíz:

```
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=postgres://user:pass@host/db
```

---

## Contacto

Profesor: Cristian Issetta | cissetta@gmail.com  
PROA Villa del Totoral – Córdoba, Argentina
