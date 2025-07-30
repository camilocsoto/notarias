from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROL_CHOICES = (
        (1, 'admin'),
        (2, 'notario'),
        (3, 'operario'),
        (4, 'cliente')
    )
    rol = models.IntegerField(choices=ROL_CHOICES)
    notaria = models.ForeignKey(
        'app.Notaria', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Notaría'
    )
    
    # para usar en la creación de superusuarios
    REQUIRED_FIELDS = ['email', 'password', 'first_name', 'last_name', 'rol']
    def save(self, *args, **kwargs):
        # Si no se define username manualmente, se asigna el valor de correo.
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.email} {self.first_name} - {self.last_name}"
