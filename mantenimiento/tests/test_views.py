from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from core.models import (
    Categoria,
    Herramienta,
    PlanMantenimiento,
    TareaMantenimiento,
    EjecucionMantenimiento,
    LogHerramienta,
)


class MantenimientoViewsTest(TestCase):

    def setUp(self):
        # ==========================================
        # CATEGORÍA
        # ==========================================

        self.categoria = Categoria.objects.create(
            nombre="Herramientas de prueba"
        )

        # ==========================================
        # HERRAMIENTA
        # ==========================================

        self.herramienta = Herramienta.objects.create(
            nombre="Taladro de prueba",
            categoria=self.categoria,
        )

        # ==========================================
        # PLAN
        # ==========================================

        self.plan = PlanMantenimiento.objects.create(
            herramienta=self.herramienta,
            nombre="Revisión del taladro",
            tipo="PREV",
            descripcion="Revisión general",
            frecuencia_dias=30,
            proxima_ejecucion=date.today() + timedelta(days=30),
            activo=True,
        )

    # ==================================================
    # INDEX
    # ==================================================

    def test_index_responde_correctamente(self):
        response = self.client.get(
            reverse("mantenimiento:index")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_index_filtra_por_herramienta(self):
        response = self.client.get(
            reverse("mantenimiento:index"),
            {
                "herramienta": self.herramienta.id
            },
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            self.plan.nombre
        )

    def test_index_filtra_por_mes(self):
        mes = self.plan.proxima_ejecucion.month

        response = self.client.get(
            reverse("mantenimiento:index"),
            {
                "mes": mes
            },
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_index_filtra_por_herramienta_y_mes(self):
        mes = self.plan.proxima_ejecucion.month

        response = self.client.get(
            reverse("mantenimiento:index"),
            {
                "herramienta": self.herramienta.id,
                "mes": mes,
            },
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # ==================================================
    # CREAR PLAN
    # ==================================================

    def test_crear_plan_get(self):
        response = self.client.get(
            reverse("mantenimiento:crear_plan")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_crear_plan_post(self):
        datos = {
            "nombre": "Mantenimiento del taladro",
            "herramienta": self.herramienta.id,
            "tipo": "PREV",
            "descripcion": "Revisión completa",
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),
        }

        response = self.client.post(
            reverse("mantenimiento:crear_plan"),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            PlanMantenimiento.objects.filter(
                nombre="Mantenimiento del taladro"
            ).exists()
        )

    def test_crear_plan_con_tareas(self):
        datos = {
            "nombre": "Plan con tareas",
            "herramienta": self.herramienta.id,
            "tipo": "PREV",
            "descripcion": "Plan de prueba",
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            "descripcion_tarea[]": [
                "Revisar motor",
                "Revisar cable",
            ],

            "responsable_tarea[]": [
                "Técnico 1",
                "Técnico 2",
            ],

            "duracion_tarea[]": [
                "20",
                "30",
            ],
        }

        response = self.client.post(
            reverse("mantenimiento:crear_plan"),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        plan = PlanMantenimiento.objects.get(
            nombre="Plan con tareas"
        )

        self.assertEqual(
            plan.tareas.count(),
            2
        )

    def test_crear_plan_sin_frecuencia(self):
        datos = {
            "nombre": "Plan sin frecuencia",
            "herramienta": self.herramienta.id,
            "tipo": "PREV",
            "descripcion": "Plan sin frecuencia",
            "frecuencia_dias": "",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),
        }

        response = self.client.post(
            reverse("mantenimiento:crear_plan"),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        plan = PlanMantenimiento.objects.get(
            nombre="Plan sin frecuencia"
        )

        self.assertIsNone(
            plan.frecuencia_dias
        )

    def test_crear_plan_sin_herramienta_muestra_error(self):
        datos = {
            "nombre": "Plan con error",
            "herramienta": 99999,
            "tipo": "PREV",
            "descripcion": "Prueba de error",
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),
        }

        response = self.client.post(
            reverse("mantenimiento:crear_plan"),
            datos,
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertFalse(
            PlanMantenimiento.objects.filter(
                nombre="Plan con error"
            ).exists()
        )

    # ==================================================
    # EJECUTAR PLAN
    # ==================================================

    def test_ejecutar_plan_get(self):
        response = self.client.get(
            reverse(
                "mantenimiento:ejecutar_plan",
                args=[self.plan.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_ejecutar_plan_post(self):
        datos = {
            "realizado_por": "Técnico de prueba",
            "es_externo": "on",
            "costo": "500",
            "notas": "Mantenimiento realizado",
        }

        response = self.client.post(
            reverse(
                "mantenimiento:ejecutar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            EjecucionMantenimiento.objects.filter(
                plan=self.plan
            ).exists()
        )

    def test_ejecutar_plan_con_tareas(self):
        tarea = TareaMantenimiento.objects.create(
            plan=self.plan,
            descripcion="Revisar motor",
            responsable="Técnico",
            duracion_estimada_min=30,
            orden=1,
        )

        datos = {
            "realizado_por": "Técnico",
            "costo": "100",
            "notas": "Todo correcto",
            "tareas_completadas": [str(tarea.id)],
        }

        response = self.client.post(
            reverse(
                "mantenimiento:ejecutar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        ejecucion = EjecucionMantenimiento.objects.get(
            plan=self.plan
        )

        self.assertTrue(
            ejecucion.tareas_completadas.filter(
                id=tarea.id
            ).exists()
        )

    # ==================================================
    # DETALLE DEL PLAN
    # ==================================================

    def test_detalle_plan_get(self):
        response = self.client.get(
            reverse(
                "mantenimiento:detalle_plan",
                args=[self.plan.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # ==================================================
    # PLAN DE VIDA
    # ==================================================

    def test_plan_de_vida_get(self):
        response = self.client.get(
            reverse(
                "mantenimiento:plan_de_vida",
                args=[self.herramienta.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # ==================================================
    # EDITAR PLAN
    # ==================================================

    def test_editar_plan_get(self):
        response = self.client.get(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_editar_plan(self):
        datos = {
            "nombre": "Plan actualizado",
            "tipo": "CORR",
            "descripcion": "Descripción actualizada",
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "60",
            "proxima_ejecucion": (
                date.today() + timedelta(days=60)
            ).strftime("%Y-%m-%d"),
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.plan.refresh_from_db()

        self.assertEqual(
            self.plan.nombre,
            "Plan actualizado"
        )

        self.assertEqual(
            self.plan.tipo,
            "CORR"
        )

        self.assertEqual(
            self.plan.frecuencia_dias,
            60
        )

    def test_editar_plan_sin_frecuencia(self):
        datos = {
            "nombre": "Plan sin frecuencia",
            "tipo": "PREV",
            "descripcion": "Plan sin frecuencia definida",
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.plan.refresh_from_db()

        self.assertIsNone(
            self.plan.frecuencia_dias
        )

    # ==================================================
    # EDITAR TAREAS
    # ==================================================

    def test_editar_tarea_existente(self):
        tarea = TareaMantenimiento.objects.create(
            plan=self.plan,
            descripcion="Descripción original",
            responsable="Responsable original",
            duracion_estimada_min=20,
            orden=1,
        )

        datos = {
            "nombre": "Plan actualizado",
            "tipo": "PREV",
            "descripcion": "Descripción nueva",
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "45",
            "proxima_ejecucion": (
                date.today() + timedelta(days=45)
            ).strftime("%Y-%m-%d"),

            f"tarea_descripcion_{tarea.id}":
                "Descripción modificada",

            f"tarea_responsable_{tarea.id}":
                "Nuevo responsable",

            f"tarea_duracion_{tarea.id}":
                "40",

            f"tarea_orden_{tarea.id}":
                "2",
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        tarea.refresh_from_db()

        self.assertEqual(
            tarea.descripcion,
            "Descripción modificada"
        )

        self.assertEqual(
            tarea.responsable,
            "Nuevo responsable"
        )

        self.assertEqual(
            tarea.duracion_estimada_min,
            40
        )

        self.assertEqual(
            tarea.orden,
            2
        )

    def test_editar_tarea_sin_duracion(self):
        tarea = TareaMantenimiento.objects.create(
            plan=self.plan,
            descripcion="Tarea de prueba",
            responsable="Técnico",
            duracion_estimada_min=30,
            orden=1,
        )

        datos = {
            "nombre": self.plan.nombre,
            "tipo": self.plan.tipo,
            "descripcion": self.plan.descripcion,
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            f"tarea_descripcion_{tarea.id}":
                "Tarea sin duración",

            f"tarea_responsable_{tarea.id}":
                "Técnico",

            f"tarea_duracion_{tarea.id}":
                "",

            f"tarea_orden_{tarea.id}":
                "1",
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        tarea.refresh_from_db()

        self.assertIsNone(
            tarea.duracion_estimada_min
        )

    def test_editar_tarea_sin_orden(self):
        tarea = TareaMantenimiento.objects.create(
            plan=self.plan,
            descripcion="Tarea de prueba",
            responsable="Técnico",
            duracion_estimada_min=30,
            orden=1,
        )

        datos = {
            "nombre": self.plan.nombre,
            "tipo": self.plan.tipo,
            "descripcion": self.plan.descripcion,
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            f"tarea_descripcion_{tarea.id}":
                "Tarea sin orden",

            f"tarea_responsable_{tarea.id}":
                "Técnico",

            f"tarea_duracion_{tarea.id}":
                "20",

            f"tarea_orden_{tarea.id}":
                "",
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        tarea.refresh_from_db()

        self.assertEqual(
            tarea.orden,
            0
        )

    def test_editar_plan_elimina_tarea(self):
        tarea = TareaMantenimiento.objects.create(
            plan=self.plan,
            descripcion="Tarea que será eliminada",
            responsable="Técnico",
            duracion_estimada_min=20,
            orden=1,
        )

        datos = {
            "nombre": self.plan.nombre,
            "tipo": self.plan.tipo,
            "descripcion": self.plan.descripcion,
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            f"tarea_eliminar_{tarea.id}": "on",
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertFalse(
            TareaMantenimiento.objects.filter(
                id=tarea.id
            ).exists()
        )

    def test_editar_plan_crea_nueva_tarea(self):
        datos = {
            "nombre": self.plan.nombre,
            "tipo": self.plan.tipo,
            "descripcion": self.plan.descripcion,
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            "nueva_tarea_descripcion": [
                "Nueva tarea de mantenimiento"
            ],

            "nueva_tarea_responsable": [
                "Técnico nuevo"
            ],

            "nueva_tarea_duracion": [
                "25"
            ],

            "nueva_tarea_orden": [
                "3"
            ],
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            TareaMantenimiento.objects.filter(
                plan=self.plan,
                descripcion="Nueva tarea de mantenimiento"
            ).exists()
        )

        tarea = TareaMantenimiento.objects.get(
            plan=self.plan,
            descripcion="Nueva tarea de mantenimiento"
        )

        self.assertEqual(
            tarea.responsable,
            "Técnico nuevo"
        )

        self.assertEqual(
            tarea.duracion_estimada_min,
            25
        )

        self.assertEqual(
            tarea.orden,
            3
        )

    def test_editar_plan_ignora_tarea_nueva_vacia(self):
        cantidad_inicial = TareaMantenimiento.objects.filter(
            plan=self.plan
        ).count()

        datos = {
            "nombre": self.plan.nombre,
            "tipo": self.plan.tipo,
            "descripcion": self.plan.descripcion,
            "herramienta": self.herramienta.id,
            "frecuencia_dias": "30",
            "proxima_ejecucion": (
                date.today() + timedelta(days=30)
            ).strftime("%Y-%m-%d"),

            "nueva_tarea_descripcion": [
                ""
            ],

            "nueva_tarea_responsable": [
                "Técnico"
            ],

            "nueva_tarea_duracion": [
                "20"
            ],

            "nueva_tarea_orden": [
                "1"
            ],
        }

        response = self.client.post(
            reverse(
                "mantenimiento:editar_plan",
                args=[self.plan.id]
            ),
            datos,
        )

        self.assertEqual(
            response.status_code,
            302
        )

        cantidad_final = TareaMantenimiento.objects.filter(
            plan=self.plan
        ).count()

        self.assertEqual(
            cantidad_inicial,
            cantidad_final
        )

    # ==================================================
    # ELIMINAR PLAN
    # ==================================================

    def test_eliminar_plan_get(self):
        response = self.client.get(
            reverse(
                "mantenimiento:eliminar_plan",
                args=[self.plan.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_eliminar_plan_post(self):
        plan_id = self.plan.id

        response = self.client.post(
            reverse(
                "mantenimiento:eliminar_plan",
                args=[plan_id]
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertFalse(
            PlanMantenimiento.objects.filter(
                id=plan_id
            ).exists()
        )

    # ==================================================
    # 404
    # ==================================================

    def test_detalle_plan_inexistente(self):
        response = self.client.get(
            reverse(
                "mantenimiento:detalle_plan",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_ejecutar_plan_inexistente(self):
        response = self.client.get(
            reverse(
                "mantenimiento:ejecutar_plan",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_editar_plan_inexistente(self):
        response = self.client.get(
            reverse(
                "mantenimiento:editar_plan",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_eliminar_plan_inexistente(self):
        response = self.client.get(
            reverse(
                "mantenimiento:eliminar_plan",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_plan_de_vida_inexistente(self):
        response = self.client.get(
            reverse(
                "mantenimiento:plan_de_vida",
                args=[99999]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )