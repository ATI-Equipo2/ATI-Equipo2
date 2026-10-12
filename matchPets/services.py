"""Lógica de negocio y consultas de matchPets, para mantener las vistas delgadas."""
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Pet, User


def obtener_feed(q=''):
    """Mascotas disponibles para adopción; si hay `q`, filtra por nombre o descripción."""
    pets = Pet.objects.filter(availableForAdoption=True).select_related('owner')
    if q:
        pets = pets.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return pets.order_by('id')


def mascotas_de(user):
    """Mascotas que pertenecen al usuario."""
    return Pet.objects.filter(owner=user).select_related('owner').order_by('id')


def buscar_mascotas(q=''):
    """Busca por nombre o por especie (acepta la etiqueta traducida, p. ej. «perro»)."""
    pets = Pet.objects.select_related('owner')
    if q:
        q_low = q.lower()
        especies = [clave for clave, etiqueta in Pet.ESPECIES
                    if q_low in clave or q_low in str(etiqueta).lower()]
        pets = pets.filter(Q(name__icontains=q) | Q(species__in=especies))
    return pets.order_by('id')


def perfil_de(username):
    """Usuario por nombre de usuario (404 si no existe)."""
    return get_object_or_404(User, username=username)
