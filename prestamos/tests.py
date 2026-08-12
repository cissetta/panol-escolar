from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Alumno, Docente, Herramienta, Prestamo


class PrestamoMultipleHerramientasTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='admin', password='admin123')
        self.alumno = Alumno.objects.create(
            nombre='Ana',
            apellido='García',
            dni='12345678',
            curso='3A',
            email='ana@test.com',
            activo=True,
        )
        self.docente = Docente.objects.create(
            nombre='Laura',
            apellido='Pérez',
            email='laura@test.com',
            activo=True,
        )
        self.herramienta_1 = Herramienta.objects.create(
            nombre='Taladro',
            descripcion='Taladro',
            marca='Bosch',
            modelo='A1',
            ubicacion='Bodega 1',
            estado='DISPONIBLE',
            activo=True,
        )
        self.herramienta_2 = Herramienta.objects.create(
            nombre='Sierra',
            descripcion='Sierra',
            marca='Makita',
            modelo='S2',
            ubicacion='Bodega 2',
            estado='DISPONIBLE',
            activo=True,
        )

    def test_crea_un_prestamo_por_herramienta_seleccionada(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('prestamos:nuevo'),
            {
                'alumno_qr': self.alumno.legajo,
                'docente': self.docente.pk,
                'herramientas': [self.herramienta_1.codigo, self.herramienta_2.codigo],
                'observaciones': 'Préstamo de prueba',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Prestamo.objects.filter(alumno=self.alumno, docente=self.docente).count(),
            2,
        )
        self.assertEqual(
            Prestamo.objects.filter(alumno=self.alumno, herramienta=self.herramienta_1).count(),
            1,
        )
        self.assertEqual(
            Prestamo.objects.filter(alumno=self.alumno, herramienta=self.herramienta_2).count(),
            1,
        )
