from django.apps import apps
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, request
from django.db.models import Q
from django.utils.translation import gettext, ngettext

Pet = apps.get_model('matchPets', 'Pet')

class LoginView(auth_views.LoginView):
    template_name = 'matchPets/login.html'
    
class LogoutView(auth_views.LogoutView):
    template_name = 'matchPets/logout.html'
    

@login_required(login_url='login')
def vista_protegida(request):
    return render(request, 'matchPets/protegida.html')

# Datos de ejemplo para las vistas de perfil (aún no hay modelos)
USUARIOS = {
    'rolando': {
        'nombre': 'Rolando',
        'edad': '20 años',
        'ubicacion': 'Los Teques',
        'descripcion': 'Soy Amante de los animales. Mi color favorito es el naranja, mi libro favorito es El hobbit, en mi tiempo libre disfruto escuchar Los fantasmas del Caribe y jugar The forest',
        'foto': 'img/perfil/rolando.png',
    },
    'jesus': {
        'nombre': 'Jesús',
        'edad': '21 años',
        'ubicacion': 'Catia',
        'descripcion': 'Considero que los humanos también somo animales, mis mascotas son compañeros de vida los cuales tienen problemas con socializar porque me da pereza pacearlos, si quieres socializar con mis mascotas tienes que ser una mamá soltera',
        'foto': 'img/perfil/jesus.png',
    },
}

MASCOTAS = {
    'ronaldo': {
        'nombre': 'Ronaldo',
        'especie': 'Perro',
        'sexo': 'Macho',
        'temperamento': 'Pansón',
        'edad': '5 años',
        'descripcion': 'Estoy Buscando a alguien que me quiera, que me huela y se emocione, que se orine por mí. Me gustan los paseos, las caricias y compartir unas chelas con mis amigos caninos.',
        'socializar': 'Estoy interesado en una perra en celo, con más de dos años, que quiera algo temporal, nada de tener familia porque me desaparezco, algo tranqui.',
        'foto': 'img/perfil/ronaldo.png',
    },
    'orlando': {
        'nombre': 'Orlando',
        'especie': 'Gato',
        'sexo': 'Macho',
        'temperamento': 'Furioso',
        'edad': '2 años',
        'foto': 'img/perfil/orlando.png',
    },
    'bruno': {
        'nombre': 'Bruno Andrés',
        'especie': 'Perro',
        'sexo': 'Macho',
        'temperamento': 'Amigable',
        'edad': '4 años',
        'foto': 'img/perfil/bruno.png',
    },
    'brown': {
        'nombre': 'Brown',
        'especie': 'Perro',
        'sexo': 'Macho',
        'temperamento': 'Juguetón',
        'edad': '2 meses',
        'descripcion': 'Hola, soy Brown. Se que no soy de la raza más grande, pero mi corazón lo es. Estoy en búsqueda de un amigo que pueda jugar conmigo sin lastimarme ya que tengo solo un par de meses de edad.',
        'socializar': 'Me gustaría conocer a un compañero canino para poder pasar el rato y compartir aventuras en el parque del este.',
        'foto': 'img/perfil/brown.png',
    },
    'lucia': {
        'nombre': 'Lucia',
        'especie': 'Gata',
        'sexo': 'Hembra',
        'temperamento': 'Cariñosa',
        'edad': '1 año',
        'foto': 'img/perfil/lucia.png',
    },
}

def signup(request):
    return render(request, 'signup.html', {'name': gettext('Registrarse')})

def login(request):
    return render(request, 'login.html', {'name': gettext('Iniciar Sesión')})

def add_pet(request):
    return render(request, 'add-pet.html', {'name': gettext('Agregar Mascota')})

def base_navigation(request):
    return render(request, 'base-navigation-desktop.html')

def base_feed_mobile(request):
    return render(request, 'base-feed-mobile.html')

def base_perfil(request):
    return render(request, 'base-perfil.html')

def perfil_usuario(request):
    return render(request, 'perfil_usuario.html', {'title': gettext('Perfil de Usuario'), 'usuario': USUARIOS['rolando']})

def ver_dueno(request):
    return render(request, 'ver_dueno.html', {'title': gettext('Ver Dueño'), 'usuario': USUARIOS['jesus']})

def perfil_mascota(request):
    return render(request, 'perfil_mascota.html', {'title': gettext('Perfil de Mascota'), 'mascota': MASCOTAS['ronaldo']})

def ver_mascota(request):
    solicitud_enviada = request.GET.get('solicitud') == 'enviada'
    return render(request, 'ver_mascota.html', {
        'title': gettext('Ver Mascota'),
        'mascota': MASCOTAS['brown'],
        'solicitud_enviada': solicitud_enviada,
        'aviso_solicitud': gettext('Solicitud enviada') if solicitud_enviada else '',
    })

def tus_mascotas(request):
    mascotas = [MASCOTAS['ronaldo'], MASCOTAS['orlando'], MASCOTAS['bruno']]
    return render(request, 'lista_mascotas.html', {'title': gettext('Tus Mascotas'), 'mascotas': mascotas, 'es_propia': True})

def sus_mascotas(request):
    mascotas = [MASCOTAS['brown'], MASCOTAS['lucia']]
    return render(request, 'lista_mascotas.html', {'title': gettext('Sus Mascotas'), 'mascotas': mascotas, 'es_propia': False})


# ---------------------------------------------------------------------------
# Datos falsos para Notificaciones / Mensajes / Solicitudes (sin backend).
# La fuente está en español; las plantillas usan {% translate %} para i18n.
# ---------------------------------------------------------------------------
NOTIFICACIONES_FALSAS = [
    {
        'id': 1,
        'tipo': 'nuevo_mensaje',
        'titulo': 'Nuevo mensaje',
        'detalle': 'Brown te envió un mensaje',
        'mascota': MASCOTAS['brown'],
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
        'foto': MASCOTAS['brown']['foto'],
    },
    {
        'nombre': 'Daisy',
        'texto': 'Hola, soy Daisy. Se que no soy de la raza más grande, pero mi coraz…',
        'foto': MASCOTAS['brown']['foto'],
    },
    {
        'nombre': 'Ronaldo',
        'texto': 'Estoy buscando a alguien que me quiera, que me huela y se emocion…',
        'foto': MASCOTAS['ronaldo']['foto'],
    },
    {
        'nombre': 'Ursula',
        'texto': 'Hola, soy Úrsula. Se que no soy de la raza más grande, pero mi…',
        'foto': MASCOTAS['lucia']['foto'],
    },
]


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


def buscar_mascotas(request):
    """Pantalla Buscar Mascotas (datos falsos, filtro por nombre/especie)."""
    q = request.GET.get('q', '').strip()
    mascotas = [MASCOTAS['brown'], MASCOTAS['ronaldo'], MASCOTAS['lucia']]
    # Daisy y Úrsula comparten la ficha del Inicio/Feed.
    extras = [m for m in MASCOTAS_INICIO if m['nombre'] in ('Daisy', 'Ursula')]
    todas = [{'nombre': m['nombre'], 'especie': m['especie'], 'foto': m['foto']} for m in mascotas] + extras
    if q:
        q_low = q.lower()
        todas = [m for m in todas if q_low in m['nombre'].lower() or q_low in m['especie'].lower()]
    return render(request, 'buscar_mascotas.html', {
        'title': gettext('Buscar Mascotas'),
        'mascotas': todas,
        'q': q,
    })


# ---------------------------------------------------------------------------
# Inicio / Feed: lista general de mascotas (modelo Pet del compañero).
# Si la tabla está vacía, se usan las fichas de las fotos (mismos datos
# falsos del resto de pantallas). El buscador filtra por nombre/especie.
# ---------------------------------------------------------------------------
MASCOTAS_INICIO = [
    {
        'nombre': 'Brown',
        'especie': 'Perro',
        'sexo': 'Macho',
        'temperamento': 'Juguetón',
        'edad': '2 meses',
        'foto': 'img/perfil/brown.png',
    },
    {
        'nombre': 'Daisy',
        'especie': 'Perro',
        'sexo': 'Hembra',
        'temperamento': 'Dormilona',
        'edad': '2 años',
        'foto': 'img/perfil/ronaldo.png',
    },
    {
        'nombre': 'Ursula',
        'especie': 'Perro',
        'sexo': 'Hembra',
        'temperamento': 'Floja',
        'edad': '3 años',
        'foto': 'img/perfil/bruno.png',
    },
    {
        'nombre': 'Lucia',
        'especie': 'Gata',
        'sexo': 'Hembra',
        'temperamento': 'Cariñosa',
        'edad': '1 año',
        'foto': 'img/perfil/lucia.png',
    },
]


def _edad_anos(cantidad):
    return ngettext('%(count)s año', '%(count)s años', cantidad) % {'count': cantidad}


def _tarjeta_desde_pet(pet):
    """Normaliza una instancia del modelo Pet al formato de la tarjeta."""
    foto_url = pet.img.url if getattr(pet, 'img', None) and pet.img else ''
    return {
        'nombre': pet.name,
        'especie': pet.get_species_display(),
        'temperamento': (pet.description or '').strip(),
        'edad': _edad_anos(pet.age),
        'sexo': pet.get_gender_display(),
        'foto_url': foto_url,
        'foto_static': '',
    }


def _tarjeta_desde_dict(mascota):
    return {
        'nombre': mascota['nombre'],
        'especie': mascota['especie'],
        'temperamento': mascota.get('temperamento', ''),
        'edad': mascota.get('edad', ''),
        'sexo': mascota.get('sexo', ''),
        'foto_url': '',
        'foto_static': mascota.get('foto', ''),
    }


def _mascotas_feed(q=''):
    """Devuelve (tarjetas, usando_datos_reales).

    Usa el modelo Pet cuando hay registros; si no, las fichas falsas.
    """
    try:
        pets = Pet.objects.filter(availableForAdoption=True).order_by('id')
        if q:
            pets = pets.filter(Q(name__icontains=q) | Q(description__icontains=q))
        tarjetas = [_tarjeta_desde_pet(p) for p in pets]
        if tarjetas:
            return tarjetas, True
    except Exception:
        # La tabla aún no existe (BD sin migrar): se usan datos falsos.
        pass
    tarjetas = [_tarjeta_desde_dict(m) for m in MASCOTAS_INICIO]
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


