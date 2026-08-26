from django.test import TestCase
from datetime import date, timedelta

from core.models import (
    Categoria,
    Herramienta,
    PlanMantenimiento,
    TareaMantenimiento,
    EjecucionMantenimiento,
    LogHerramienta
)


class PlanMantenimientoTest(TestCase):

    def setUp(self):
        # Creamos una categoría de prueba
        self.categoria = Categoria.objects.create(
            nombre="Herramientas de prueba"
        )

        # Creamos una herramienta de prueba
        self.herramienta = Herramienta.objects.create(
            nombre="Taladro de prueba",
            categoria=self.categoria
        )

    def test_crear_plan_mantenimiento(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Revisión del taladro",
            tipo="PREV",
            descripcion="Revisión general de la herramienta",
            frecuencia_dias=30,
            proxima_ejecucion=date.today() + timedelta(days=30),
            activo=True
        )

        self.assertEqual(plan.nombre, "Revisión del taladro")
        self.assertEqual(plan.tipo, "PREV")
        self.assertEqual(plan.frecuencia_dias, 30)
        self.assertTrue(plan.activo)
        self.assertEqual(plan.herramienta, self.herramienta)

    def test_mantenimiento_vencido(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento vencido",
            tipo="PREV",
            descripcion="Prueba de mantenimiento vencido",
            frecuencia_dias=30,
            proxima_ejecucion=date.today() - timedelta(days=1),
            activo=True
        )

        self.assertTrue(plan.esta_vencido())

    def test_mantenimiento_proximo(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento próximo",
            tipo="PREV",
            descripcion="Mantenimiento próximo",
            frecuencia_dias=30,
            proxima_ejecucion=date.today() + timedelta(days=3),
            activo=True
        )

        self.assertTrue(plan.esta_proximo())

    def test_avanzar_proxima_ejecucion(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento programado",
            tipo="PREV",
            descripcion="Prueba de actualización de fecha",
            frecuencia_dias=30,
            proxima_ejecucion=date.today(),
            activo=True
        )

        plan.avanzar_proxima_ejecucion()

        fecha_esperada = date.today() + timedelta(days=30)

        self.assertEqual(
            plan.proxima_ejecucion,
            fecha_esperada
        )

    def test_crear_tarea_mantenimiento(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento del taladro",
            tipo="PREV",
            descripcion="Mantenimiento general",
            frecuencia_dias=30,
            proxima_ejecucion=date.today() + timedelta(days=30),
            activo=True
        )

        tarea = TareaMantenimiento.objects.create(
            plan=plan,
            descripcion="Revisar el cable de alimentación",
            responsable="Técnico",
            duracion_estimada_min=20,
            orden=1
        )

        self.assertEqual(tarea.plan, plan)
        self.assertEqual(
            tarea.descripcion,
            "Revisar el cable de alimentación"
        )
        self.assertEqual(tarea.responsable, "Técnico")
        self.assertEqual(tarea.duracion_estimada_min, 20)
        self.assertEqual(tarea.orden, 1)

    def test_crear_ejecucion_actualiza_proxima_fecha(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento del taladro",
            tipo="PREV",
            descripcion="Mantenimiento preventivo",
            frecuencia_dias=30,
            proxima_ejecucion=date.today(),
            activo=True
        )

        ejecucion = EjecucionMantenimiento.objects.create(
            plan=plan,
            realizado_por="Técnico de prueba",
            es_externo=False,
            costo=1500,
            notas="Mantenimiento realizado correctamente"
        )

        plan.refresh_from_db()

        fecha_esperada = date.today() + timedelta(days=30)

        self.assertEqual(
            plan.proxima_ejecucion,
            fecha_esperada
        )

        self.assertEqual(
            ejecucion.realizado_por,
            "Técnico de prueba"
        )

        self.assertEqual(ejecucion.costo, 1500)

    def test_mantenimiento_correctivo_deja_herramienta_disponible(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Reparación del taladro",
            tipo="CORR",
            descripcion="Reparación correctiva",
            frecuencia_dias=30,
            proxima_ejecucion=date.today(),
            activo=True
        )

        self.herramienta.cambiar_estado("REPARACION")

        EjecucionMantenimiento.objects.create(
            plan=plan,
            realizado_por="Técnico de prueba",
            es_externo=False,
            costo=2500,
            notas="Reparación finalizada"
        )

        self.herramienta.refresh_from_db()

        self.assertEqual(
            self.herramienta.estado,
            "DISPONIBLE"
        )

    def test_ejecucion_crea_log_herramienta(self):
        plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Mantenimiento del taladro",
            tipo="PREV",
            descripcion="Mantenimiento preventivo",
            frecuencia_dias=30,
            proxima_ejecucion=date.today(),
            activo=True
        )

        EjecucionMantenimiento.objects.create(
            plan=plan,
            realizado_por="Técnico de prueba",
            es_externo=False,
            costo=1500,
            notas="Mantenimiento realizado"
        )

        log = LogHerramienta.objects.filter(
            herramienta=self.herramienta,
            tipo="MANTENIMIENTO"
        ).last()

        self.assertIsNotNone(log)
        self.assertIn(
            "Mantenimiento Preventivo ejecutado",
            log.descripcion
        )
        self.assertIn(
            "Técnico de prueba",
            log.descripcion
        )