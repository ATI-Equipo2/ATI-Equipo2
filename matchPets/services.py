"""Lógica de negocio y consultas de matchPets, para mantener las vistas delgadas."""
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext

from .models import FriendshipRequest, Message, Notification, Pet, User


def obtener_feed(q=''):
    """Mascotas disponibles para adopción; si hay `q`, filtra por nombre o descripción."""
    pets = Pet.objects.filter(availableForAdoption=True).select_related('owner')
    if q:
        q_low = q.lower()
        especies = [clave for clave, etiqueta in Pet.ESPECIES
            if q_low in clave.lower() or q_low in str(etiqueta).lower()]
        pets = pets.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(species__in=especies)
        )
    return pets.order_by('id')


def mascotas_de(user):
    """Mascotas que pertenecen al usuario."""
    return Pet.objects.filter(owner=user).select_related('owner').order_by('id')


def buscar_mascotas(q=''):
    """Busca por nombre, descripción o especie (acepta la etiqueta traducida, p. ej. «perro»)."""
    pets = Pet.objects.select_related('owner')
    if q:
        q_low = q.lower()
        especies = [clave for clave, etiqueta in Pet.ESPECIES
                    if q_low in clave or q_low in str(etiqueta).lower()]
        pets = pets.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(species__in=especies)
        )
    return pets.order_by('id')


def perfil_de(username):
    """Usuario por nombre de usuario (404 si no existe)."""
    return get_object_or_404(User, username=username)


def _nombre_de(user):
    return user.nombre or user.username


@transaction.atomic
def crear_solicitud(from_user, from_pet, to_pet):
    """Crea la solicitud de socialización y notifica al dueño de la mascota destino."""
    solicitud = FriendshipRequest.objects.create(
        from_user=from_user,
        to_user=to_pet.owner,
        from_pet=from_pet,
        to_pet=to_pet,
    )
    Notification.objects.create(
        user=to_pet.owner,
        tipo='solicitud_recibida',
        titulo=gettext('Tienes una solicitud de %(nombre)s') % {'nombre': _nombre_de(from_user)},
        detalle=gettext('%(origen)s quiere socializar con %(destino)s') % {
            'origen': from_pet.name,
            'destino': to_pet.name,
        },
        pet=from_pet,
        solicitud=solicitud,
    )
    return solicitud


@transaction.atomic
def resolver_solicitud(solicitud, aceptar):
    """Acepta o rechaza la solicitud y notifica al emisor."""
    solicitud.status = 'accepted' if aceptar else 'rejected'
    solicitud.save(update_fields=['status'])
    # La notificación original ya fue atendida.
    solicitud.notifications.update(leida=True)
    if aceptar:
        tipo = 'solicitud_aceptada'
        titulo = gettext('Solicitud aceptada')
        detalle = gettext('%(mascota)s aceptó tu solicitud')
    else:
        tipo = 'solicitud_denegada'
        titulo = gettext('Solicitud denegada')
        detalle = gettext('%(mascota)s denegó tu solicitud')
    Notification.objects.create(
        user=solicitud.from_user,
        tipo=tipo,
        titulo=titulo,
        detalle=detalle % {'mascota': solicitud.to_pet.name},
        pet=solicitud.to_pet,
        solicitud=solicitud,
    )
    return solicitud


def pueden_chatear(user1, user2):
    """True si existe una solicitud de socialización aceptada entre ambos usuarios."""
    if user1.id == user2.id:
        return False
    return FriendshipRequest.objects.filter(
        Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1),
        status='accepted',
    ).exists()


def conversaciones_de(user):
    """Lista las conversaciones del usuario, desde la más reciente.

    Cada elemento es un dict con: usuario (el otro participante),
    ultimo_mensaje y no_leidos.
    """
    qs = (Message.objects
          .filter(Q(sender=user) | Q(receiver=user))
          .select_related('sender', 'receiver')
          .order_by('-created_at'))

    conversaciones = {}
    for mensaje in qs:
        otro = mensaje.receiver if mensaje.sender_id == user.id else mensaje.sender
        if otro.id not in conversaciones:
            conversaciones[otro.id] = {
                'usuario': otro,
                'ultimo_mensaje': mensaje,
                'no_leidos': 0,
            }
        if mensaje.receiver_id == user.id and not mensaje.read:
            conversaciones[otro.id]['no_leidos'] += 1

    return list(conversaciones.values())


@transaction.atomic
def enviar_mensaje(de_user, para_user, contenido):
    """Crea el mensaje y notifica al destinatario (una sola notificación por remitente sin leer)."""
    mensaje = Message.objects.create(
        sender=de_user,
        receiver=para_user,
        content=contenido,
    )
    ya_notificado = Notification.objects.filter(
        user=para_user,
        tipo='mensaje',
        from_user=de_user,
        leida=False,
    ).exists()
    if not ya_notificado:
        Notification.objects.create(
            user=para_user,
            tipo='mensaje',
            from_user=de_user,
            titulo=gettext('Nuevo mensaje de %(nombre)s') % {'nombre': _nombre_de(de_user)},
            detalle=contenido[:120],
        )
    return mensaje
