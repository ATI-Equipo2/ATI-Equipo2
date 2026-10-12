"""Puebla la base de datos con usuarios y mascotas de ejemplo (los mismos para todo el equipo).

Uso:
    python manage.py seed_data           # crea/actualiza los datos de ejemplo
    python manage.py seed_data --flush   # borra antes los datos existentes
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from matchPets import services
from matchPets.models import FriendshipRequest, Message, Notification, Pet, User

PASSWORD = 'test1234'
IMG_DIR = Path(settings.BASE_DIR) / 'matchPets' / 'static' / 'img' / 'perfil'

USUARIOS = {
    'rolando': {
        'nombre': 'Rolando',
        'email': 'rolando@example.com',
        'edad': 20,
        'ubicacion': 'Los Teques',
        'descripcion': 'Soy Amante de los animales. Mi color favorito es el naranja, mi libro favorito es El hobbit, en mi tiempo libre disfruto escuchar Los fantasmas del Caribe y jugar The forest',
        'foto': 'rolando.png',
    },
    'jesus': {
        'nombre': 'Jesús',
        'email': 'jesus@example.com',
        'edad': 21,
        'ubicacion': 'Catia',
        'descripcion': 'Considero que los humanos también somo animales, mis mascotas son compañeros de vida los cuales tienen problemas con socializar porque me da pereza pacearlos, si quieres socializar con mis mascotas tienes que ser una mamá soltera',
        'foto': 'jesus.png',
    },
}

# (dueño, nombre, especie, sexo, edad en años, temperamento, descripción, socializar, foto)
MASCOTAS = [
    ('rolando', 'Ronaldo', 'dog', 'male', 5, 'Pansón',
     'Estoy Buscando a alguien que me quiera, que me huela y se emocione, que se orine por mí. Me gustan los paseos, las caricias y compartir unas chelas con mis amigos caninos.',
     'Estoy interesado en una perra en celo, con más de dos años, que quiera algo temporal, nada de tener familia porque me desaparezco, algo tranqui.',
     'ronaldo.png'),
    ('rolando', 'Orlando', 'cat', 'male', 2, 'Furioso',
     'Gato de pocos amigos, pero fiel con quien se lo gana.', '', 'orlando.png'),
    ('rolando', 'Bruno Andrés', 'dog', 'male', 4, 'Amigable',
     'Siempre listo para jugar con quien se cruce en su camino.', '', 'bruno.png'),
    ('jesus', 'Brown', 'dog', 'male', 0, 'Juguetón',
     'Hola, soy Brown. Se que no soy de la raza más grande, pero mi corazón lo es. Estoy en búsqueda de un amigo que pueda jugar conmigo sin lastimarme ya que tengo solo un par de meses de edad.',
     'Me gustaría conocer a un compañero canino para poder pasar el rato y compartir aventuras en el parque del este.',
     'brown.png'),
    ('jesus', 'Lucia', 'cat', 'female', 1, 'Cariñosa',
     'Una gata muy dulce a la que le encanta dormir en tu regazo.', '', 'lucia.png'),
    ('jesus', 'Daisy', 'dog', 'female', 2, 'Dormilona',
     'Pasa el día durmiendo, pero despierta para los paseos.', '', 'ronaldo.png'),
    ('jesus', 'Ursula', 'dog', 'female', 3, 'Floja',
     'Prefiere el sofá antes que el parque.', '', 'bruno.png'),
]


def _adjuntar_imagen(campo, nombre_archivo):
    """Copia una imagen estática al ImageField si todavía no tiene archivo."""
    if campo:
        return
    ruta = IMG_DIR / nombre_archivo
    if ruta.exists():
        with ruta.open('rb') as f:
            campo.save(nombre_archivo, File(f), save=False)


class Command(BaseCommand):
    help = 'Crea usuarios y mascotas de ejemplo para desarrollo (contraseña de los usuarios: test1234).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Borra mascotas, notificaciones, solicitudes, mensajes y usuarios no administradores antes de sembrar.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self._borrar_datos()

        usuarios = {}
        for username, datos in USUARIOS.items():
            user, _ = User.objects.get_or_create(username=username, defaults={'email': datos['email']})
            for campo in ('nombre', 'email', 'edad', 'ubicacion', 'descripcion'):
                setattr(user, campo, datos[campo])
            user.set_password(PASSWORD)
            _adjuntar_imagen(user.foto, datos['foto'])
            user.save()
            usuarios[username] = user

        mascotas = {}
        for (dueno, nombre, especie, sexo, edad, temperamento,
             descripcion, socializar, foto) in MASCOTAS:
            pet, _ = Pet.objects.get_or_create(
                name=nombre, owner=usuarios[dueno],
                defaults={'species': especie, 'gender': sexo, 'age': edad},
            )
            pet.species, pet.gender, pet.age = especie, sexo, edad
            pet.temperament, pet.description, pet.socialization = temperamento, descripcion, socializar
            pet.availableForAdoption = True
            _adjuntar_imagen(pet.img, foto)
            pet.save()
            mascotas[nombre] = pet

        # Una solicitud pendiente de ejemplo para probar notificaciones.
        origen, destino = mascotas['Brown'], mascotas['Ronaldo']
        if not FriendshipRequest.objects.filter(from_pet=origen, to_pet=destino).exists():
            services.crear_solicitud(usuarios['jesus'], origen, destino)

        self.stdout.write(self.style.SUCCESS(
            f'Datos de prueba listos: {len(usuarios)} usuarios, {len(mascotas)} mascotas '
            f'(usuarios: {", ".join(usuarios)}; contraseña: {PASSWORD}).'
        ))

    def _borrar_datos(self):
        Notification.objects.all().delete()
        FriendshipRequest.objects.all().delete()
        Message.objects.all().delete()
        # Se borran también los archivos subidos de lo que se elimina.
        for pet in Pet.objects.all():
            if pet.img:
                pet.img.delete(save=False)
        Pet.objects.all().delete()
        # Los superusuarios (p. ej. admin) se conservan.
        for user in User.objects.filter(is_superuser=False):
            if user.foto:
                user.foto.delete(save=False)
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Datos existentes eliminados (superusuarios conservados).')
