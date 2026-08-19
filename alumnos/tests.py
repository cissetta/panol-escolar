from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Alumno
from datetime import date

class AlumnoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', password='test123')
        self.client.force_login(self.user)
 
    def test_lista_solo_activos(self):
        Alumno.objects.create(nombre='Juan', apellido='Pérez', dni='12345678', curso='3A', email='juan@proa.edu.ar', fecha_alta=date.today(), activo=False)
        response = self.client.get('/alumnos/')
        self.assertEqual(len(response.context['page_obj']), 0)
 
    def test_busqueda_por_dni(self):
        Alumno.objects.create(nombre='Ana', apellido='García', dni='98765432', curso='3A', email='ana@proa.edu.ar', fecha_alta=date.today())
        response = self.client.get('/alumnos/?q=98765432')
        self.assertEqual(len(response.context['page_obj']), 1)
 
    def test_dni_duplicado_rechazado(self):
        Alumno.objects.create(nombre='Pedro', apellido='López', dni='11111111', curso='3A', email='pedro@proa.edu.ar', fecha_alta=date.today())
        response = self.client.post('/alumnos/nuevo/', {
            'nombre': 'Carlos', 'apellido': 'Ruiz', 'dni': '11111111', 'curso': '5A', 'email': 'carlos@proa.edu.ar'
        })
        self.assertFormError(response, 'form', 'dni', 'Ya existe un alumno con DNI 11111111.')