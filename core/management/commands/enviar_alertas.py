"""
core/management/commands/enviar_alertas.py

Comando Django para enviar alertas por email:
  - Préstamos vencidos no notificados
  - Insumos con stock crítico (stock_actual <= stock_minimo)

Uso:
    python manage.py enviar_alertas           # envío normal
    python manage.py enviar_alertas --test    # imprime en consola sin enviar
    python manage.py enviar_alertas --forzar  # re-envía aunque ya estén notificados

Programar con cron (diario a las 8 AM):
    0 8 * * * cd /ruta/proyecto && python manage.py enviar_alertas >> /var/log/panol_alertas.log 2>&1
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from core.models import ConfiguracionSistema, Prestamo, Insumo


class Command(BaseCommand):
    help = 'Envía alertas por email: préstamos vencidos e insumos con stock crítico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Muestra las alertas en consola sin enviar emails ni actualizar base de datos',
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Re-envía alertas aunque los préstamos ya hayan sido notificados antes',
        )

    def handle(self, *args, **options):
        config = ConfiguracionSistema.get()

        if not config.email_alertas:
            raise CommandError(
                'No hay email de alertas configurado. '
                'Ingresá a Admin → Configuración del Sistema y completá "Email alertas".'
            )

        es_test  = options['test']
        forzar   = options['forzar']

        # ── 1. Préstamos vencidos ─────────────────────────────────
        limite = timezone.now() - timedelta(days=config.dias_maximo_prestamo)
        qs_prestamos = Prestamo.objects.filter(
            fecha_devolucion__isnull=True,
            fecha_prestamo__lt=limite,
        ).select_related('alumno', 'herramienta', 'docente')

        if not forzar:
            qs_prestamos = qs_prestamos.filter(notificado_vencimiento=False)

        prestamos_vencidos = list(qs_prestamos)

        # ── 2. Insumos críticos ───────────────────────────────────
        insumos_criticos = [i for i in Insumo.objects.filter(activo=True) if i.es_critico]

        if not prestamos_vencidos and not insumos_criticos:
            self.stdout.write(self.style.SUCCESS('✓ Sin alertas pendientes. No se envió ningún email.'))
            return

        # ── 3. Armar cuerpo del email ─────────────────────────────
        lineas = [
            f'SISTEMA DE PAÑOL – {config.nombre_institucion}',
            f'Reporte de alertas al {timezone.now().strftime("%d/%m/%Y %H:%M")}',
            '=' * 60,
            '',
        ]

        if prestamos_vencidos:
            lineas += [
                f'⚠ PRÉSTAMOS VENCIDOS ({len(prestamos_vencidos)})',
                '-' * 40,
            ]
            for p in prestamos_vencidos:
                exceso = timezone.now() - (p.fecha_prestamo + timedelta(days=config.dias_maximo_prestamo))
                horas  = int(exceso.total_seconds() // 3600)
                lineas.append(
                    f'  • {p.alumno}  →  {p.herramienta.nombre} [{p.herramienta.codigo}]'
                    f'  |  Desde: {p.fecha_prestamo.strftime("%d/%m/%Y %H:%M")}'
                    f'  |  Demora: +{horas}h'
                    f'  |  Docente: {p.docente}'
                )
            lineas.append('')

        if insumos_criticos:
            lineas += [
                f'⚠ INSUMOS CON STOCK CRÍTICO ({len(insumos_criticos)})',
                '-' * 40,
            ]
            for ins in insumos_criticos:
                lineas.append(
                    f'  • {ins.nombre} [{ins.codigo}]'
                    f'  |  Stock actual: {ins.stock_actual} {ins.get_unidad_display()}'
                    f'  |  Stock mínimo: {ins.stock_minimo} {ins.get_unidad_display()}'
                )
            lineas.append('')

        lineas += [
            '─' * 60,
            'Ingresá al sistema para gestionar estas situaciones.',
        ]

        cuerpo = '\n'.join(lineas)
        asunto = (
            f'[Pañol {config.nombre_institucion}] '
            f'Alertas: {len(prestamos_vencidos)} préstamos vencidos, '
            f'{len(insumos_criticos)} insumos críticos'
        )

        # ── 4. Enviar o mostrar ───────────────────────────────────
        if es_test:
            self.stdout.write(self.style.WARNING('── MODO TEST: no se envía email ──'))
            self.stdout.write(f'Destinatario: {config.email_alertas}')
            self.stdout.write(f'Asunto: {asunto}')
            self.stdout.write('')
            self.stdout.write(cuerpo)
            return

        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=None,  # usa DEFAULT_FROM_EMAIL de settings
                recipient_list=[config.email_alertas],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f'Error al enviar email: {exc}')

        # ── 5. Marcar préstamos como notificados ──────────────────
        if prestamos_vencidos and not forzar:
            ids = [p.pk for p in prestamos_vencidos]
            Prestamo.objects.filter(pk__in=ids).update(notificado_vencimiento=True)

        self.stdout.write(self.style.SUCCESS(
            f'✓ Email enviado a {config.email_alertas} '
            f'({len(prestamos_vencidos)} préstamos, {len(insumos_criticos)} insumos críticos)'
        ))
