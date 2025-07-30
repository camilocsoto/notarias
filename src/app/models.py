from django.db import models
from accounts.models import User


class Notaria(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    isActive = models.BooleanField(default=True)
    cantidad_empleados = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.nombre} has {self.cantidad_empleados} with tel {self.telefono}'

class TipoTicket(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    letra = models.CharField(max_length=1, default='A')
    ultimo_numero = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.letra}-{self.ultimo_numero}"

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('llamado', 'Llamado'),
        ('atendiendo', 'Atendiendo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    numero_turno = models.CharField(max_length=10, unique=True)
    tipo_servicio = models.ForeignKey(TipoTicket, on_delete=models.CASCADE)

    comments = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 4},
        related_name='tickets_como_cliente'       # ← related_name distinto
    )
    operador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 3},
        related_name='tickets_como_operador'      # ← related_name distinto
    )
    notaria = models.ForeignKey(
        'app.Notaria',
        on_delete=models.CASCADE,
        related_name='tickets'                   # opcional: para acceder desde Notaria
    )

    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo_servicio', 'estado']),
            models.Index(fields=['notaria', 'estado']),
        ]

    def save(self, *args, **kwargs):
        # ...
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero_turno