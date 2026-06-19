"""
settings.py – Configuración del proyecto Pañol Escolar
PROA Villa del Totoral – Programación IV 2026

⚠️  Este archivo es provisto por el Tech Lead.
    No modificar sin consultar, especialmente INSTALLED_APPS y AUTH.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SEGURIDAD ───────────────────────────────────────────────────
# En producción: cambiar por un valor secreto y poner DEBUG=False
SECRET_KEY = 'django-insecure-panol-proa-villa-totoral-2026-cambiar-en-produccion'
DEBUG = True
ALLOWED_HOSTS = ['*']  # En producción: ['192.168.1.X', 'localhost']

# ─── APPS INSTALADAS ─────────────────────────────────────────────
# Los grupos deben agregar sus apps aquí al crearlas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto (Tech Lead)
    'accounts',   # Login, logout, roles
    'core',       # Modelos compartidos, dashboard base

    # Apps de los grupos – descomentar al crear la app
    'alumnos',        # Grupo 1
    'inventario',     # Grupo 2
    'prestamos',      # Grupo 3
    'mantenimiento',  # Grupo 4
    'reportes',       # Grupo 5
]

# ─── MIDDLEWARE ──────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'panol_escolar.urls'

# ─── TEMPLATES ───────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # templates globales en raíz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'panol_escolar.wsgi.application'

# ─── BASE DE DATOS ───────────────────────────────────────────────
# SQLite para desarrollo. Migrar a PostgreSQL para producción.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── VALIDACIÓN DE CONTRASEÑAS ───────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNACIONALIZACIÓN ────────────────────────────────────────
LANGUAGE_CODE = 'es-ar'
TIME_ZONE     = 'America/Argentina/Cordoba'
USE_I18N      = True
USE_TZ        = True

# ─── ARCHIVOS ESTÁTICOS ──────────────────────────────────────────
STATIC_URL        = '/static/'
STATICFILES_DIRS  = [BASE_DIR / 'static']
STATIC_ROOT       = BASE_DIR / 'staticfiles'

# ─── ARCHIVOS MEDIA (QR, imágenes) ──────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── AUTENTICACIÓN ───────────────────────────────────────────────
LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
