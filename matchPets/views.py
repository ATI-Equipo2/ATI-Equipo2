from django.shortcuts import render

from django.http import HttpResponse
from django.utils.translation import gettext

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
    # Añadimos Daisy y Úrsula como datos falsos solo para esta pantalla.
    extras = [
        {'nombre': 'Daisy', 'especie': 'Perro', 'foto': MASCOTAS['brown']['foto']},
        {'nombre': 'Ursula', 'especie': 'Perro', 'foto': MASCOTAS['lucia']['foto']},
    ]
    todas = [{'nombre': m['nombre'], 'especie': m['especie'], 'foto': m['foto']} for m in mascotas] + extras
    if q:
        q_low = q.lower()
        todas = [m for m in todas if q_low in m['nombre'].lower() or q_low in m['especie'].lower()]
    return render(request, 'buscar_mascotas.html', {
        'title': gettext('Buscar Mascotas'),
        'mascotas': todas,
        'q': q,
    })
