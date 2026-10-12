from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.utils.translation import gettext, ngettext

from . import mock_data, services
from .forms import PetForm, RegistroForm
from .models import Pet, User


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
    return render(request, 'base-navigation-desktop.html')


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
    solicitud_enviada = request.GET.get('solicitud') == 'enviada'
    return render(request, 'ver_mascota.html', {
        'title': gettext('Ver Mascota'),
        'mascota': _tarjeta_desde_pet(pet),
        'solicitud_enviada': solicitud_enviada,
        'aviso_solicitud': gettext('Solicitud enviada') if solicitud_enviada else '',
    })


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
# Datos falsos para Notificaciones / Mensajes / Solicitudes (sin backend).
# Se reemplazan por el ORM en la fase de notificaciones.
# La fuente está en español; las plantillas usan {% translate %} para i18n.
# ---------------------------------------------------------------------------
NOTIFICACIONES_FALSAS = [
    {
        'id': 1,
        'tipo': 'nuevo_mensaje',
        'titulo': 'Nuevo mensaje',
        'detalle': 'Brown te envió un mensaje',
        'mascota': None,
    },
    {
        'id': 2,
        'tipo': 'solicitud_aceptada',
        'titulo': 'Solicitud aceptada',
        'detalle': 'Daisy aceptó tu solicitud',
        'mascota': None,
    },
    {
        'id': 3,
        'tipo': 'solicitud_recibida',
        'titulo': 'Tienes una solicitud de Nora',
        'detalle': 'Nora quiere socializar con Brown',
        'mascota': None,
        'solicitante': 'Nora',
    },
]

MENSAJES_RECIENTES_FALSOS = [
    {
        'nombre': 'Brown',
        'texto': 'Hola, soy Brown. Se que no soy de la raza más grande, pero mi…',
        'foto': 'img/perfil/brown.png',
    },
    {
        'nombre': 'Daisy',
        'texto': 'Hola, soy Daisy. Se que no soy de la raza más grande, pero mi coraz…',
        'foto': 'img/perfil/brown.png',
    },
    {
        'nombre': 'Ronaldo',
        'texto': 'Estoy buscando a alguien que me quiera, que me huela y se emocion…',
        'foto': 'img/perfil/ronaldo.png',
    },
    {
        'nombre': 'Ursula',
        'texto': 'Hola, soy Úrsula. Se que no soy de la raza más grande, pero mi…',
        'foto': 'img/perfil/lucia.png',
    },
]


@login_required(login_url='login')
def notificaciones(request):
    """Pantalla de Notificaciones / Solicitudes / Mensajes (datos falsos).

    Query params (solo para previsualizar estados sin backend):
      ?estado=solicitud_enviada  -> muestra aviso "Solicitud enviada"
      ?estado=solicitud_aceptada -> muestra aviso "Solicitud aceptada"
      ?estado=solicitud_denegada -> muestra aviso "Solicitud denegada"
    La interacción Aceptar/Denegar/Cerrar también funciona en el navegador
    con JavaScript, sin recargar.
    """
    estado = request.GET.get('estado', '')
    avisos = {
        'solicitud_enviada': gettext('Solicitud enviada'),
        'solicitud_aceptada': gettext('Solicitud aceptada'),
        'solicitud_denegada': gettext('Solicitud denegada'),
        'mensaje_nuevo': gettext('Nuevo mensaje'),
    }
    return render(request, 'notificaciones.html', {
        'title': gettext('Notificaciones'),
        'notificaciones': NOTIFICACIONES_FALSAS,
        'mensajes_recientes': MENSAJES_RECIENTES_FALSOS,
        'aviso_inicial': avisos.get(estado, ''),
        'hay_no_leidas': True,
    })


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
