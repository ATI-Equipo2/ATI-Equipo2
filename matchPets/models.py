from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

# Modelo de Mascota (propuesto por el compañero; se respetan sus campos).
# El texto fuente está en español y se traduce al inglés vía gettext_lazy.
class Pet(models.Model):
    ESPECIES = [
        ('dog', _('Perro')),
        ('cat', _('Gato')),
        ('bird', _('Ave')),
        ('other', _('Otro')),
    ]

    GENEROS = [
        ('male', _('Macho')),
        ('female', _('Hembra')),
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=ESPECIES, default='dog')
    age = models.IntegerField(help_text=_("Edad en años"))
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENEROS, default='male')
    img = models.ImageField(upload_to='pets/', blank=True, null=True)
    availableForAdoption = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.species})"
    
    
class User(AbstractUser):
    nombre = models.CharField(max_length=100, blank=True)


