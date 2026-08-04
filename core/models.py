"""
core/models.py – Modelos centrales del Sistema de Pañol Escolar
PROA Villa del Totoral – Programación IV 2026

⚠️  Archivo provisto por el Tech Lead. No modificar sin consultar.
    Los grupos EXTIENDEN estos modelos desde sus propias apps si es necesario.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date, timedelta


# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════════════════

class ConfiguracionSistema(models.Model):
    nombre_institucion       = models.CharField(max_length=100, default='PROA Villa del Totoral')
    dias_maximo_prestamo     = models.PositiveIntegerField(default=2)
    dias_aviso_mantenimiento = models.PositiveIntegerField(default=7)
    email_alertas            = models.EmailField(blank=True)

    class Meta:
        verbose_name        = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'

    def __str__(self):
        return self.nombre_institucion

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ══════════════════════════════════════════════════════════════════
#  DOCENTES
# ══════════════════════════════════════════════════════════════════

class Docente(models.Model):
    nombre   = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email    = models.EmailField(unique=True)
    activo   = models.BooleanField(default=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'


# ══════════════════════════════════════════════════════════════════
#  ALUMNOS  (Grupo 1)
# ══════════════════════════════════════════════════════════════════

class Alumno(models.Model):
    CURSOS = [
        ('3A','3° A'), ('3B','3° B'),
        ('4A','4° A'), ('4B','4° B'),
        ('5A','5° A'), ('5B','5° B'),
        ('6A','6° A'), ('6B','6° B'), # <-- Agregados 6to año
        ('7A','7° A'), ('7B','7° B'), # <-- Agregados 7mo año
    ]
    legajo   = models.CharField(max_length=10, unique=True, blank=True)
    nombre   = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni      = models.CharField(max_length=10, unique=True)
    curso    = models.CharField(max_length=2, choices=CURSOS)
    email    = models.EmailField(blank=True)
    qr_code  = models.ImageField(upload_to='qr/alumnos/', null=True, blank=True)
    activo   = models.BooleanField(default=True)
    fecha_alta = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f'{self.apellido}, {self.nombre} ({self.get_curso_display()})'

    def save(self, *args, **kwargs):
        if not self.legajo:
            ultimo = Alumno.objects.order_by('id').last()
            num = (ultimo.id + 1) if ultimo else 1
            self.legajo = f'ALU-{num:04d}'
        super().save(*args, **kwargs)

    def prestamos_activos(self):
        return self.prestamo_set.filter(fecha_devolucion__isnull=True)

    def tiene_prestamo_vencido(self):
        config = ConfiguracionSistema.get()
        limite = timezone.now() - timedelta(days=config.dias_maximo_prestamo)
        return self.prestamos_activos().filter(fecha_prestamo__lt=limite).exists()
# ══════════════════════════════════════════════════════════════════
#  INVENTARIO  (Grupo 2)
# ══════════════════════════════════════════════════════════════════

class Categoria(models.Model):
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    color_hex   = models.CharField(max_length=7, default='#2E86DE')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Herramienta(models.Model):
    ESTADOS = [
        ('DISPONIBLE','Disponible'),
        ('PRESTADA',  'Prestada'),
        ('REPARACION','En Reparación'),
        ('BAJA',      'Baja'),
    ]
    codigo      = models.CharField(max_length=20, unique=True, blank=True)
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    marca       = models.CharField(max_length=50, blank=True)
    modelo      = models.CharField(max_length=50, blank=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.SET_NULL,
                    null=True, blank=True, related_name='herramientas')
    ubicacion   = models.CharField(max_length=50, blank=True)
    estado      = models.CharField(max_length=15, choices=ESTADOS, default='DISPONIBLE')
    fecha_compra = models.DateField(null=True, blank=True)
    costo       = models.DecimalField(max_digits=12, decimal_places=2,
                    null=True, blank=True, validators=[MinValueValidator(0)])
    qr_code     = models.ImageField(upload_to='qr/herramientas/', null=True, blank=True)
    fecha_alta  = models.DateField(auto_now_add=True)
    activo      = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'

    def __str__(self):
        return f'{self.nombre} [{self.codigo}]'

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultima = Herramienta.objects.order_by('id').last()
            num = (ultima.id + 1) if ultima else 1
            self.codigo = f'HRR-{num:04d}'
        super().save(*args, **kwargs)

    def esta_disponible(self):
        return self.estado == 'DISPONIBLE'

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self.save()
        LogHerramienta.objects.create(
            herramienta=self,
            tipo='ESTADO',
            descripcion=f'Estado cambiado a {self.get_estado_display()}'
        )


class LogHerramienta(models.Model):
    TIPOS = [
        ('ALTA',         'Alta en inventario'),
        ('ESTADO',       'Cambio de estado'),
        ('PRESTAMO',     'Préstamo'),
        ('DEVOLUCION',   'Devolución'),
        ('MANTENIMIENTO','Mantenimiento'),
        ('BAJA',         'Baja'),
    ]
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE,
                    related_name='log_eventos')
    tipo        = models.CharField(max_length=15, choices=TIPOS)
    descripcion = models.TextField()
    fecha       = models.DateTimeField(auto_now_add=True)
    usuario     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Evento de Herramienta'
        verbose_name_plural = 'Historial de Herramientas'

    def __str__(self):
        return f'{self.herramienta} – {self.get_tipo_display()} ({self.fecha:%d/%m/%Y})'


class Insumo(models.Model):
    UNIDADES = [
        ('unidad','Unidad'), ('metros','Metros'), ('litros','Litros'),
        ('gramos','Gramos'), ('hojas','Hojas'),   ('rollos','Rollos'),
    ]
    codigo       = models.CharField(max_length=20, unique=True, blank=True)
    nombre       = models.CharField(max_length=100)
    descripcion  = models.TextField(blank=True)
    categoria    = models.ForeignKey(Categoria, on_delete=models.SET_NULL,
                     null=True, blank=True, related_name='insumos')
    unidad       = models.CharField(max_length=10, choices=UNIDADES, default='unidad')
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                     validators=[MinValueValidator(0)])
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                     validators=[MinValueValidator(0)])
    activo       = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'

    def __str__(self):
        return f'{self.nombre} ({self.stock_actual} {self.unidad})'

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Insumo.objects.order_by('id').last()
            num = (ultimo.id + 1) if ultimo else 1
            self.codigo = f'INS-{num:04d}'
        super().save(*args, **kwargs)

    @property
    def es_critico(self):
        return self.stock_actual <= self.stock_minimo


class MovimientoInsumo(models.Model):
    TIPOS = [
        ('ENTRADA','Entrada de stock'),
        ('ENTREGA','Entrega a alumno'),
        ('AJUSTE', 'Ajuste manual'),
    ]
    insumo      = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    tipo        = models.CharField(max_length=10, choices=TIPOS)
    cantidad    = models.DecimalField(max_digits=10, decimal_places=2)
    fecha       = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True)
    usuario     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento de Insumo'
        verbose_name_plural = 'Movimientos de Insumos'

    def __str__(self):
        return f'{self.insumo.nombre} – {self.get_tipo_display()} ({self.cantidad})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.tipo == 'ENTRADA':
            self.insumo.stock_actual += self.cantidad
        else:
            self.insumo.stock_actual -= self.cantidad
        self.insumo.save()


# ══════════════════════════════════════════════════════════════════
#  PRÉSTAMOS  (Grupo 3)
# ══════════════════════════════════════════════════════════════════

class Prestamo(models.Model):
    ESTADOS_DEVOLUCION = [
        ('BUEN_ESTADO', 'Buen estado'),
        ('DESGASTE',    'Desgaste leve'),
        ('REPARACION',  'Requiere reparación'),
        ('DANIO_GRAVE', 'Dañada gravemente'),
    ]
    alumno      = models.ForeignKey(Alumno, on_delete=models.PROTECT)
    herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT)
    docente     = models.ForeignKey(Docente, on_delete=models.PROTECT)
    fecha_prestamo   = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado_devolucion = models.CharField(max_length=15, choices=ESTADOS_DEVOLUCION,
                          null=True, blank=True)
    observaciones    = models.TextField(blank=True)
    notificado_vencimiento = models.BooleanField(default=False)
    modulo_clase     = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-fecha_prestamo']
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'

    def __str__(self):
        estado = 'Activo' if self.esta_activo() else 'Devuelto'
        return f'{self.alumno} – {self.herramienta} [{estado}]'

    def esta_activo(self):
        return self.fecha_devolucion is None

    def estado_label(self):
        """Devuelve una tupla (texto, clase_badge) para mostrar el estado en las vistas.

        - Si está devuelto: 'Devuelto (Estado)' con clase 'success'.
        - Si está activo y vencido según la configuración: '+{horas}h préstamo vencido' con 'danger'.
        - Si está activo y no vencido: 'Activo' con 'primary'.
        """
        if not self.esta_activo():
            estado = self.get_estado_devolucion_display() if self.estado_devolucion else 'Devuelto'
            return (f'Devuelto ({estado})', 'success')

        # Está activo
        config = ConfiguracionSistema.get()
        limite = self.fecha_prestamo + timedelta(days=config.dias_maximo_prestamo)
        ahora = timezone.now()
        if ahora > limite:
            exceso = ahora - limite
            horas = int(exceso.total_seconds() // 3600)
            return (f'+{horas}h préstamo vencido', 'danger')
        return ('Activo', 'primary')

    def esta_vencido(self):
        if not self.esta_activo():
            return False
        config = ConfiguracionSistema.get()
        limite = timezone.now() - timedelta(days=config.dias_maximo_prestamo)
        return self.fecha_prestamo < limite

    def registrar_devolucion(self, estado, observaciones=''):
        self.fecha_devolucion = timezone.now()
        self.estado_devolucion = estado
        self.observaciones = observaciones
        self.save()
        if estado in ('REPARACION', 'DANIO_GRAVE'):
            self.herramienta.cambiar_estado('REPARACION')
        else:
            self.herramienta.cambiar_estado('DISPONIBLE')
        LogHerramienta.objects.create(
            herramienta=self.herramienta,
            tipo='DEVOLUCION',
            descripcion=f'Devuelto por {self.alumno}. Estado: {self.get_estado_devolucion_display()}. {observaciones}'
        )


class PrestamoInsumo(models.Model):
    alumno      = models.ForeignKey(Alumno, on_delete=models.PROTECT)
    insumo      = models.ForeignKey(Insumo, on_delete=models.PROTECT)
    docente     = models.ForeignKey(Docente, on_delete=models.PROTECT)
    cantidad    = models.DecimalField(max_digits=10, decimal_places=2,
                    validators=[MinValueValidator(0.01)])
    fecha       = models.DateTimeField(default=timezone.now)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Entrega de Insumo'
        verbose_name_plural = 'Entregas de Insumos'

    def __str__(self):
        return f'{self.alumno} – {self.insumo.nombre} ({self.cantidad})'


# ══════════════════════════════════════════════════════════════════
#  MANTENIMIENTO  (Grupo 4)
# ══════════════════════════════════════════════════════════════════

class PlanMantenimiento(models.Model):
    TIPOS = [('PREV','Preventivo'), ('CORR','Correctivo')]
    herramienta       = models.ForeignKey(Herramienta, on_delete=models.CASCADE,
                          related_name='planes_mantenimiento')
    nombre            = models.CharField(max_length=100)
    tipo              = models.CharField(max_length=4, choices=TIPOS)
    descripcion       = models.TextField(blank=True)
    frecuencia_dias   = models.PositiveIntegerField(null=True, blank=True)
    proxima_ejecucion = models.DateField()
    activo            = models.BooleanField(default=True)

    class Meta:
        ordering = ['proxima_ejecucion']
        verbose_name = 'Plan de Mantenimiento'
        verbose_name_plural = 'Planes de Mantenimiento'

    def __str__(self):
        return f'{self.nombre} – {self.herramienta}'

    def esta_vencido(self):
        return self.proxima_ejecucion < date.today()

    def esta_proximo(self):
        config = ConfiguracionSistema.get()
        limite = date.today() + timedelta(days=config.dias_aviso_mantenimiento)
        return date.today() <= self.proxima_ejecucion <= limite

    def avanzar_proxima_ejecucion(self):
        if self.frecuencia_dias:
            self.proxima_ejecucion = date.today() + timedelta(days=self.frecuencia_dias)
            self.save()


class TareaMantenimiento(models.Model):
    plan        = models.ForeignKey(PlanMantenimiento, on_delete=models.CASCADE,
                    related_name='tareas')
    descripcion = models.CharField(max_length=200)
    responsable = models.CharField(max_length=100, blank=True)
    duracion_estimada_min = models.PositiveIntegerField(null=True, blank=True)
    orden       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Tarea de Mantenimiento'
        verbose_name_plural = 'Tareas de Mantenimiento'

    def __str__(self):
        return f'{self.plan} – {self.descripcion}'


class EjecucionMantenimiento(models.Model):
    plan               = models.ForeignKey(PlanMantenimiento, on_delete=models.CASCADE,
                           related_name='ejecuciones')
    fecha              = models.DateField(default=date.today)
    realizado_por      = models.CharField(max_length=100, blank=True)
    es_externo         = models.BooleanField(default=False)
    costo              = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                           validators=[MinValueValidator(0)])
    notas              = models.TextField(blank=True)
    tareas_completadas = models.ManyToManyField(TareaMantenimiento, blank=True,
                           related_name='ejecuciones')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Ejecución de Mantenimiento'
        verbose_name_plural = 'Ejecuciones de Mantenimiento'

    def __str__(self):
        return f'{self.plan} – {self.fecha}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.plan.avanzar_proxima_ejecucion()
        if self.plan.tipo == 'CORR':
            self.plan.herramienta.cambiar_estado('DISPONIBLE')
        LogHerramienta.objects.create(
            herramienta=self.plan.herramienta,
            tipo='MANTENIMIENTO',
            descripcion=(
                f'Mantenimiento {self.plan.get_tipo_display()} ejecutado. '
                f'Plan: {self.plan.nombre}. '
                f'Realizado por: {self.realizado_por or "No especificado"}. '
                f'Costo: ${self.costo}. {self.notas}'
            )
        )
