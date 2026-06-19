from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    """
    Extiende el User de Django con el rol del sistema.
    Se crea automáticamente via signal al crear un User.
    """
    ROLES = [
        ('ADMIN',    'Administrador'),
        ('PANOLERO', 'Pañolero'),
        ('DOCENTE',  'Docente'),
        ('ALUMNO',   'Alumno'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol  = models.CharField(max_length=10, choices=ROLES, default='PANOLERO')

    class Meta:
        verbose_name        = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def __str__(self):
        return f'{self.user.username} – {self.get_rol_display()}'

    def es_admin(self):    return self.rol == 'ADMIN'
    def es_panolero(self): return self.rol == 'PANOLERO'
    def es_docente(self):  return self.rol == 'DOCENTE'
    def es_alumno(self):   return self.rol == 'ALUMNO'
