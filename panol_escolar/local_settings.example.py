"""
local_settings.py – Configuración local (NO versionar, agregar a .gitignore)

INSTRUCCIONES PARA ACTIVAR EL EMAIL:
1. Copiá este archivo como local_settings.py en la misma carpeta.
2. Completá EMAIL_HOST_USER con la cuenta Gmail del pañol.
3. En Gmail → Seguridad → Verificación en dos pasos (activar).
4. En Gmail → Seguridad → Contraseñas de aplicación → crear una para "Django Pañol".
5. Pegá esa contraseña de 16 caracteres en EMAIL_HOST_PASSWORD (sin espacios).
6. Ejecutá: python manage.py enviar_alertas --test  para verificar.

Ejemplo de cuenta: panol.proa.totoral@gmail.com
"""

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'panol.proa.totoral@gmail.com'       # ← tu cuenta Gmail
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'                # ← contraseña de aplicación (16 chars)
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER
