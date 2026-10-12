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
    temperament = models.CharField(_("Temperamento"), max_length=100, blank=True, default='')
    socialization = models.TextField(_("En busca de socializar"), blank=True, default='')
    gender = models.CharField(max_length=20, choices=GENEROS, default='male')
    img = models.ImageField(upload_to='pets/', blank=True, null=True)
    availableForAdoption = models.BooleanField(default=True)
    owner = models.ForeignKey(
        'matchPets.User',
        on_delete=models.CASCADE,
        related_name='pets',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.species})"
    
    
class User(AbstractUser):
    nombre = models.CharField(max_length=100, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    ubicacion = models.CharField(max_length=150, blank=True, default='')
    descripcion = models.TextField(blank=True, default='')
    foto = models.ImageField(upload_to='users/', null=True, blank=True)





class FriendshipRequest(models.Model):
    ESTADOS = [
        ('pending', _('Pendiente')),
        ('accepted', _('Aceptada')),
        ('rejected', _('Rechazada')),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    from_pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='sent_requests')
    to_pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=ESTADOS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_pet} -> {self.to_pet} ({self.status})"


class Notification(models.Model):
    TIPOS = [
        ('mensaje', _('Mensaje')),
        ('solicitud_recibida', _('Solicitud recibida')),
        ('solicitud_aceptada', _('Solicitud aceptada')),
        ('solicitud_denegada', _('Solicitud denegada')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    detalle = models.TextField(blank=True, default='')
    leida = models.BooleanField(default=False)
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True, blank=True)
    # Solicitud asociada (permite aceptar/denegar desde la notificación).
    solicitud = models.ForeignKey(
        FriendshipRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.titulo}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"
