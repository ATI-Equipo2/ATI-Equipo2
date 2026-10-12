from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.http import Http404
from django.views.decorators.http import require_POST
from django.utils.translation import gettext, ngettext

from . import mock_data, services
from .forms import PetForm, RegistroForm
from .models import FriendshipRequest, Notification, Pet, User


class LoginView(auth_views.LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = gettext('Iniciar Sesión')
        return context


# Django 5 exige POST para cerrar sesión; redirige a LOGOUT_REDIRECT_URL.
class LogoutView(auth_views.LogoutView):
    pass


@login_required(login_url='login')
def vista_protegida(request):
    return render(request, 'matchPets/protegida.html')


# ---------------------------------------------------------------------------
# Helpers para presentar modelos en las plantillas
# ---------------------------------------------------------------------------
def _edad_anos(cantidad):
    return ngettext('%(count)s año', '%(count)s años', cantidad) % {'count': cantidad}


def _tarjeta_desde_pet(pet):
    """Normaliza una instancia del modelo Pet al formato que esperan las plantillas."""
    descripcion = (pet.description or '').strip()
    return {
        'id': pet.id,
        'nombre': pet.name,
        'especie': pet.get_species_display(),
        'sexo': pet.get_gender_display(),
        'edad': _edad_anos(pet.age),
        'temperamento': pet.temperament,
        'descripcion': descripcion,
        'socializar': (pet.socialization or '').strip(),
        'dueno_id': pet.owner_id,
        'foto_url': pet.img.url if pet.img else '',
        'foto_static': '',
    }


def _tarjeta_desde_mock(mascota):
    """Normaliza una ficha de mock_data (fallback sin base de datos)."""
    return {
        'id': None,
        'nombre': mascota['nombre'],
        'especie': mascota['especie'],
        'sexo': '',
        'edad': _edad_anos(mascota['edad']),
        'temperamento': mascota.get('descripcion', ''),
        'descripcion': mascota.get('descripcion', ''),
        'socializar': '',
        'dueno_id': None,
        'foto_url': mascota.get('foto', ''),
        'foto_static': '',
    }


def _contexto_usuario(usuario, title):
    return {
        'title': title,
        'usuario': usuario,
        'edad_texto': _edad_anos(usuario.edad) if usuario.edad is not None else '',
    }


# ---------------------------------------------------------------------------
# Autenticación y páginas base
# ---------------------------------------------------------------------------
def signup(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('feed')
    else:
        form = RegistroForm()
    return render(request, 'signup.html', {'name': gettext('Registrarse'), 'form': form})


@login_required(login_url='login')
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, gettext('Mascota agregada correctamente'))
            return redirect('tus_mascotas')
    else:
        form = PetForm()
    return render(request, 'add-pet.html', {'name': gettext('Agregar Mascota'), 'form': form})


def base_navigation(request):
    return render(request, 'base-navegacion-desktop.html')


def base_feed_mobile(request):
    return render(request, 'base-feed-mobile.html')


def base_perfil(request):
    return render(request, 'base-perfil.html')


# ---------------------------------------------------------------------------
# Perfiles de usuario
# ---------------------------------------------------------------------------
@login_required(login_url='login')
def perfil_usuario(request):
    return render(request, 'perfil_usuario.html', _contexto_usuario(request.user, gettext('Perfil de Usuario')))


@login_required(login_url='login')
def ver_dueno(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    return render(request, 'ver_dueno.html', _contexto_usuario(usuario, gettext('Ver Dueño')))


# ---------------------------------------------------------------------------
# Mascotas
# ---------------------------------------------------------------------------
@login_required(login_url='login')
def perfil_mascota(request, pet_id):
    """Perfil de una mascota propia; si es ajena se muestra la vista pública."""
    pet = get_object_or_404(Pet, pk=pet_id)
    if pet.owner_id != request.user.id:
        return redirect('ver_mascota', pet_id=pet.id)
    return render(request, 'perfil_mascota.html', {
        'title': gettext('Perfil de Mascota'),
        'mascota': _tarjeta_desde_pet(pet),
    })


@login_required(login_url='login')
def ver_mascota(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)
    es_propia = pet.owner_id == request.user.id
    return render(request, 'ver_mascota.html', {
        'title': gettext('Ver Mascota'),
        'mascota': _tarjeta_desde_pet(pet),
        'es_propia': es_propia,
        'mis_mascotas': [] if es_propia else list(services.mascotas_de(request.user)),
    })


@login_required(login_url='login')
@require_POST
def enviar_solicitud(request, pet_id):
    """Envía una solicitud de socialización a una mascota ajena."""
    to_pet = get_object_or_404(Pet.objects.select_related('owner'), pk=pet_id)
    destino = redirect('ver_mascota', pet_id=to_pet.id)
    if to_pet.owner_id is None or to_pet.owner_id == request.user.id:
        messages.error(request, gettext('No puedes enviar una solicitud a esta mascota'))
        return destino

    mis_mascotas = list(services.mascotas_de(request.user))
    elegida = request.POST.get('from_pet', '')
    from_pet = next((p for p in mis_mascotas if str(p.id) == elegida), None)
    if from_pet is None and len(mis_mascotas) == 1:
        from_pet = mis_mascotas[0]
    if from_pet is None:
        messages.error(request, gettext('Elige una de tus mascotas para enviar la solicitud'))
        return destino

    if FriendshipRequest.objects.filter(from_pet=from_pet, to_pet=to_pet, status='pending').exists():
        messages.info(request, gettext('Ya enviaste una solicitud pendiente a esta mascota'))
        return destino

    services.crear_solicitud(request.user, from_pet, to_pet)
    messages.success(request, gettext('Solicitud enviada'))
    return destino


@login_required(login_url='login')
def tus_mascotas(request):
    mascotas = [_tarjeta_desde_pet(p) for p in services.mascotas_de(request.user)]
    return render(request, 'lista_mascotas.html', {
        'title': gettext('Tus Mascotas'),
        'mascotas': mascotas,
        'es_propia': True,
    })


@login_required(login_url='login')
def sus_mascotas(request, user_id):
    dueno = get_object_or_404(User, pk=user_id)
    mascotas = [_tarjeta_desde_pet(p) for p in services.mascotas_de(dueno)]
    return render(request, 'lista_mascotas.html', {
        'title': gettext('Sus Mascotas'),
        'mascotas': mascotas,
        'es_propia': False,
        'dueno': dueno,
    })


@login_required(login_url='login')
def buscar_mascotas(request):
    """Pantalla Buscar Mascotas: filtra por nombre o especie."""
    q = request.GET.get('q', '').strip()
    mascotas = [_tarjeta_desde_pet(p) for p in services.buscar_mascotas(q)]
    return render(request, 'buscar_mascotas.html', {
        'title': gettext('Buscar Mascotas'),
        'mascotas': mascotas,
        'q': q,
    })


# ---------------------------------------------------------------------------
# Notificaciones y solicitudes
# ---------------------------------------------------------------------------
@login_required(login_url='login')
def notificaciones(request):
    """Pantalla de Notificaciones / Solicitudes del usuario."""
    lista = (Notification.objects.filter(user=request.user)
             .select_related('pet', 'solicitud').order_by('-created_at'))
    return render(request, 'notificaciones.html', {
        'title': gettext('Notificaciones'),
        'notificaciones': lista,
        'no_leidas': lista.filter(leida=False).count(),
    })


@login_required(login_url='login')
@require_POST
def responder_solicitud(request, req_id, accion):
    """El destinatario acepta o deniega una solicitud pendiente."""
    if accion not in ('aceptar', 'denegar'):
        raise Http404
    solicitud = get_object_or_404(FriendshipRequest, pk=req_id, to_user=request.user)
    if solicitud.status != 'pending':
        messages.info(request, gettext('Esta solicitud ya fue respondida'))
    else:
        services.resolver_solicitud(solicitud, aceptar=(accion == 'aceptar'))
        messages.success(request, gettext('Solicitud aceptada') if accion == 'aceptar'
                         else gettext('Solicitud denegada'))
    return redirect('notificaciones')


@login_required(login_url='login')
@require_POST
def marcar_leida(request, notif_id):
    Notification.objects.filter(id=notif_id, user=request.user).update(leida=True)
    return redirect('notificaciones')


@login_required(login_url='login')
@require_POST
def descartar_notificacion(request, notif_id):
    Notification.objects.filter(id=notif_id, user=request.user).delete()
    return redirect('notificaciones')


# ---------------------------------------------------------------------------
# Inicio / Feed: lista general de mascotas disponibles.
# Si no hay mascotas (o la tabla aún no existe) se usan las fichas de
# mock_data como fallback temporal; esas tarjetas no enlazan a ningún perfil.
# ---------------------------------------------------------------------------
def _mascotas_feed(q=''):
    """Devuelve (tarjetas, usando_datos_reales)."""
    try:
        if Pet.objects.exists():
            return [_tarjeta_desde_pet(p) for p in services.obtener_feed(q)], True
    except DatabaseError:
        # La tabla aún no existe (BD sin migrar): se usan datos falsos.
        pass
    tarjetas = [_tarjeta_desde_mock(m) for m in mock_data.MASCOTAS_FALSAS]
    if q:
        q_low = q.lower()
        tarjetas = [t for t in tarjetas
                    if q_low in t['nombre'].lower() or q_low in t['especie'].lower()]
    return tarjetas, False


def feed(request):
    """Pantalla principal: Inicio / Feed con buscador y tarjetas."""
    q = request.GET.get('q', '').strip()
    tarjetas, usando_datos_reales = _mascotas_feed(q)
    return render(request, 'feed.html', {
        'title': gettext('Inicio'),
        'mascotas': tarjetas,
        'q': q,
        'usando_datos_reales': usando_datos_reales,
    })


def inicio(request):
    """Alias de la pantalla principal (la vista Home del sistema)."""
    return feed(request)
