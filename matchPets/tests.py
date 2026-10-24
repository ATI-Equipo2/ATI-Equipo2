import io
from PIL import Image
import tempfile
import shutil

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from matchPets.models import Pet, Notification, FriendshipRequest
from matchPets import services
from matchPets.forms import RegistroForm
from django.urls import reverse
from django.utils.translation import override

from django.core.files.uploadedfile import SimpleUploadedFile



User = get_user_model()

#Tests para modelos
class PetModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='dueñoprueba',
            email='dueno@example.com',
            password='Password123*',
            nombre='Carlos'
        )

    def test_crear_mascota(self):
        """Verifica que se pueda crear una mascota asociada a un usuario."""
        pet = Pet.objects.create(
            name='Firulais',
            species='dog',
            age=3,
            gender='male',
            temperament='Juguetón',
            description='Un perrito muy amigable.',
            owner=self.user
        )

        self.assertEqual(pet.name, 'Firulais')
        self.assertEqual(pet.species, 'dog')
        self.assertEqual(pet.owner, self.user)
        
        self.assertEqual(str(pet), 'Firulais (dog)')

#Tests para Formularios de Registro
class RegistroFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'esteban_quito',
            'email': 'esteban@quito.com',
            'nombre': 'Esteban Quito',
            'password1': 'contrasena123*',
            'password2': 'contrasena123*',
        }

    def test_formulario_save_crea_usuario_correctamente(self):
        """Prueba unitaria: el método save() crea el usuario y encripta la contraseña."""
        form = RegistroForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'esteban_quito')
        self.assertEqual(user.email, 'esteban@quito.com')
        self.assertEqual(user.nombre, 'Esteban Quito')
        # Verifica que la contraseña no se guarde en texto plano sino hasheada
        self.assertTrue(user.check_password('contrasena123*'))
        self.assertNotEqual(user.password, 'contrasena123*')

    def test_formulario_invalido_si_contrasenas_no_coinciden(self):
        """Prueba unitaria: la validación rechaza contraseñas no coincidentes."""
        data = self.valid_data.copy()
        data['password2'] = 'otraContrasena123*'
        form = RegistroForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_formulario_requiere_email_y_nombre(self):
        """Prueba unitaria: valida que email y nombre sean obligatorios en RegistroForm."""
        data = self.valid_data.copy()
        data['email'] = ''
        data['nombre'] = ''
        form = RegistroForm(data=data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('nombre', form.errors)

    def test_formulario_invalido_con_username_duplicado(self):
        """Prueba unitaria: no permite registrar un usuario cuyo username ya exista."""
        # Creamos un usuario previo
        User.objects.create_user(
            username='esteban_quito',
            email='otro@example.com',
            password='Password123*',
            nombre='Otro Nombre'
        )

        form = RegistroForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

# Tests para autenticación
class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )

    def test_login_get_renderiza_formulario(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Usuario')
        self.assertContains(resp, 'Contraseña')

    def test_login_post_valido_autentica_y_redirige(self):
        resp = self.client.post(reverse('login'), {
            'username': 'rolando',
            'password': 'test1234',
        })
        self.assertRedirects(resp, reverse('feed'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_post_password_incorrecta_no_autentica(self):
        resp = self.client.post(reverse('login'), {
            'username': 'rolando',
            'password': 'incorrecta',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_post_username_inexistente_no_autentica(self):
        resp = self.client.post(reverse('login'), {
            'username': 'noexiste',
            'password': 'test1234',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_respeta_parametro_next(self): #Verifica que despues del login vaya (segun el next) a la pagina especificada (tus_mascotas)
        resp = self.client.post(
            reverse('login') + '?next=' + reverse('tus_mascotas'),
            {'username': 'rolando', 'password': 'test1234'},
        )
        self.assertRedirects(resp, reverse('tus_mascotas'))

    def test_login_ya_autenticado_redirige_al_feed(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('login'))
        self.assertRedirects(resp, reverse('feed'))


class LogoutTests(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )

    def test_logout_por_get_devuelve_405(self):
        # Django 5 exige POST para cerrar sesión; GET debe rechazarse.
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('logout'))
        self.assertEqual(resp.status_code, 405)

    def test_logout_por_post_cierra_sesion(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(reverse('logout'))
        self.assertRedirects(resp, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class ProtectedViewsTests(TestCase):
    #Cada vista privada debe redirigir a login con ?next= cuando no hay sesión.

    def test_agregar_mascota_requiere_login(self):
        resp = self.client.get(reverse('agregar_mascota'))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('agregar_mascota')}",
        )

    def test_tus_mascotas_requiere_login(self):
        resp = self.client.get(reverse('tus_mascotas'))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('tus_mascotas')}",
        )

    def test_notificaciones_requiere_login(self):
        resp = self.client.get(reverse('notificaciones'))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('notificaciones')}",
        )

    def test_perfil_usuario_requiere_login(self):
        resp = self.client.get(reverse('perfil_usuario'))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('perfil_usuario')}",
        )

    def test_feed_es_publico(self): #Dejamos el feed público por si un usuario le interesa ver el veed antes de registrarse
        resp = self.client.get(reverse('feed'))
        self.assertEqual(resp.status_code, 200)

# Tests de  feed y búsqueda
class FeedTests(TestCase):
    def setUp(self):
        self.pet_perro = Pet.objects.create(
            name='Firulais',
            species='dog',
            age=3,
            description='Un perro jugueton',
            availableForAdoption=True,
        )
        self.pet_gato = Pet.objects.create(
            name='Michi',
            species='cat',
            age=2,
            description='Una gata tranquila',
            availableForAdoption=True,
        )
        self.pet_no_disponible = Pet.objects.create(
            name='Rex',
            species='dog',
            age=5,
            availableForAdoption=False,
        )

    def test_feed_sin_q_muestra_solo_disponibles(self):
        resp = self.client.get(reverse('feed'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Firulais')
        self.assertContains(resp, 'Michi')
        self.assertNotContains(resp, 'Rex') #No deberia atrapar a Rex porque no tiene availableForAdoption y el feed sólo muestra ésas

    def test_feed_filtra_por_nombre(self):
        resp = self.client.get(reverse('feed'), {'q': 'Firulais'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')
        self.assertNotContains(resp, 'Rex')

    def test_feed_filtra_por_especie_etiqueta_espanol(self):
        """Regresión: buscar 'perro' debe encontrar species='dog'."""
        resp = self.client.get(reverse('feed'), {'q': 'perro'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_feed_filtra_por_especie_etiqueta_ingles(self):
        with override('en'):
            resp = self.client.get(reverse('feed'), {'q': 'dog'}) #Forzamos el idioma a EN y verificamos, para probar idioams
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    #Misma prueba anterior pero en el idioma defecto actual
    def test_feed_filtra_por_especie_clave_cruda(self):
        resp = self.client.get(reverse('feed'), {'q': 'dog'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_feed_sin_resultados_no_rompe(self):
        resp = self.client.get(reverse('feed'), {'q': 'ornitorrinco'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')
        self.assertContains(resp, 'Sin resultados')


# Tests de agregar mascota
class AddPetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )
        self.temp_media = tempfile.mkdtemp() #Creamos un directorio para no ensuciar el directorio de la aplicación en cada ejecución de los tests
        self.addCleanup(shutil.rmtree, self.temp_media, True) #Agregamos un cleanup para ése directorio
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media) #Hacemos override a la configuración para que use ese directorio
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)

    def test_agregar_mascota_get_renderiza_formulario(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('agregar_mascota'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Agregar Mascota')

    def test_agregar_mascota_post_crea_pet_con_owner(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(reverse('agregar_mascota'), {
            'name': 'Firulais',
            'species': 'dog',
            'gender': 'male',
            'age': 3,
            'temperament': 'Juguetón',
            'description': 'Un perro',
            'socialization': '',
        })
        self.assertRedirects(resp, reverse('tus_mascotas'))
        self.assertEqual(Pet.objects.count(), 1)
        pet = Pet.objects.get(name='Firulais')
        self.assertEqual(pet.owner, self.user)

    def test_agregar_mascota_post_invalido_no_crea(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(reverse('agregar_mascota'), {
            'name': '',
            'species': 'dog',
            'gender': 'male',
            'age': 3,
            'temperament': '',
            'description': '',
            'socialization': '',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Pet.objects.count(), 0)


    def test_agregar_mascota_acepta_imagen(self):
        self.client.login(username='rolando', password='test1234')

        buf = io.BytesIO()
        Image.new('RGB', (1, 1), color='red').save(buf, format='PNG')


        imagen = SimpleUploadedFile(
            'firulais.png',
            buf.getvalue(),
            content_type='image/png',
        )
        resp = self.client.post(reverse('agregar_mascota'), {
            'name': 'Firulais',
            'species': 'dog',
            'gender': 'male',
            'age': 3,
            'temperament': 'Juguetón',
            'description': '',
            'socialization': '',
            'img': imagen,
        })
        self.assertRedirects(resp, reverse('tus_mascotas'))
        pet = Pet.objects.get(name='Firulais')
        self.assertTrue(pet.img)
        self.assertTrue(pet.img.name.startswith('pets/'))

# Tests de notificaciones
class NotificationContextProcessorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )

    def test_usuario_anonimo_recibe_cero(self):
        resp = self.client.get(reverse('feed'))
        self.assertEqual(resp.context['unread_notifications_count'], 0)
        self.assertEqual(resp.context['recent_notifications'], [])

    def test_usuario_con_notificaciones_cuenta_solo_no_leidas(self):
        Notification.objects.create(
            user=self.user, tipo='mensaje', titulo='N1', leida=False,
        )
        Notification.objects.create(
            user=self.user, tipo='mensaje', titulo='N2', leida=False,
        )
        Notification.objects.create(
            user=self.user, tipo='mensaje', titulo='N3', leida=True,
        )
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('feed'))
        self.assertEqual(resp.context['unread_notifications_count'], 2)
        self.assertEqual(len(resp.context['recent_notifications']), 3)

    def test_recent_notifications_devuelve_maximo_cinco(self):
        for i in range(7):
            Notification.objects.create(
                user=self.user, tipo='mensaje', titulo=f'N{i}', leida=False,
            )
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('feed'))
        self.assertEqual(resp.context['unread_notifications_count'], 7)
        self.assertEqual(len(resp.context['recent_notifications']), 5)


class NotificacionesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )
        self.otro = User.objects.create_user(
            username='jesus',
            email='jesus@example.com',
            password='test1234',
            nombre='Jesús',
        )
        self.mia = Notification.objects.create(
            user=self.user, tipo='mensaje', titulo='Mía', leida=False,
        )
        self.ajena = Notification.objects.create(
            user=self.otro, tipo='mensaje', titulo='Ajena', leida=False,
        )
        self.client.login(username='rolando', password='test1234')

    def test_muestra_solo_mis_notificaciones(self):
        resp = self.client.get(reverse('notificaciones'))
        self.assertContains(resp, 'Mía')
        self.assertNotContains(resp, 'Ajena')

    def test_marcar_leida_actualiza_propia(self):
        self.client.post(reverse('marcar_leida', args=[self.mia.id]))
        self.mia.refresh_from_db()
        self.assertTrue(self.mia.leida)

    def test_marcar_leida_ajena_no_hace_nada(self):
        self.client.post(reverse('marcar_leida', args=[self.ajena.id]))
        self.ajena.refresh_from_db()
        self.assertFalse(self.ajena.leida)

    def test_descartar_borra_propia(self):
        self.client.post(reverse('descartar_notificacion', args=[self.mia.id]))
        self.assertFalse(Notification.objects.filter(id=self.mia.id).exists())
        self.assertTrue(Notification.objects.filter(id=self.ajena.id).exists())

    def test_descartar_ajena_no_hace_nada(self):
        self.client.post(reverse('descartar_notificacion', args=[self.ajena.id]))
        self.assertTrue(Notification.objects.filter(id=self.ajena.id).exists())

    def test_mutar_notificacion_por_get_devuelve_405(self):
        self.assertEqual(
            self.client.get(reverse('marcar_leida', args=[self.mia.id])).status_code,
            405,
        )
        self.assertEqual(
            self.client.get(
                reverse('descartar_notificacion', args=[self.mia.id])
            ).status_code,
            405,
        )


class SolicitudFlowTests(TestCase):
    def setUp(self):
        self.rolando = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
        )
        self.jesus = User.objects.create_user(
            username='jesus',
            email='jesus@example.com',
            password='test1234',
            nombre='Jesús',
        )
        self.pet_rolando = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.rolando,
        )
        self.pet_jesus = Pet.objects.create(
            name='Brown', species='dog', age=1, owner=self.jesus,
        )

    def test_enviar_solicitud_crea_request_y_notificacion(self):
        self.client.login(username='rolando', password='test1234')
        self.client.post(
            reverse('enviar_solicitud', args=[self.pet_jesus.id]),
            {'from_pet': self.pet_rolando.id},
        )
        self.assertEqual(FriendshipRequest.objects.count(), 1)
        solicitud = FriendshipRequest.objects.first()
        self.assertEqual(solicitud.from_user, self.rolando)
        self.assertEqual(solicitud.to_user, self.jesus)
        self.assertEqual(solicitud.status, 'pending')
        self.assertEqual(
            Notification.objects.filter(
                user=self.jesus, tipo='solicitud_recibida',
            ).count(),
            1,
        )

    def test_no_se_puede_enviar_a_mascota_propia(self):
        self.client.login(username='rolando', password='test1234')
        self.client.post(
            reverse('enviar_solicitud', args=[self.pet_rolando.id]),
            {'from_pet': self.pet_rolando.id},
        )
        self.assertEqual(FriendshipRequest.objects.count(), 0)

    def test_no_se_duplica_solicitud_pendiente(self):
        self.client.login(username='rolando', password='test1234')
        self.client.post(
            reverse('enviar_solicitud', args=[self.pet_jesus.id]),
            {'from_pet': self.pet_rolando.id},
        )
        self.client.post(
            reverse('enviar_solicitud', args=[self.pet_jesus.id]),
            {'from_pet': self.pet_rolando.id},
        )
        self.assertEqual(FriendshipRequest.objects.count(), 1)

    def test_aceptar_solicitud_cambia_estado_y_notifica_al_emisor(self):
        solicitud = services.crear_solicitud(
            self.rolando, self.pet_rolando, self.pet_jesus,
        )
        self.client.login(username='jesus', password='test1234')
        self.client.post(
            reverse('responder_solicitud', args=[solicitud.id, 'aceptar'])
        )
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.status, 'accepted')
        self.assertEqual(
            Notification.objects.filter(
                user=self.rolando, tipo='solicitud_aceptada',
            ).count(),
            1,
        )

    def test_denegar_solicitud_cambia_estado_y_notifica_al_emisor(self):
        solicitud = services.crear_solicitud(
            self.rolando, self.pet_rolando, self.pet_jesus,
        )
        self.client.login(username='jesus', password='test1234')
        self.client.post(
            reverse('responder_solicitud', args=[solicitud.id, 'denegar'])
        )
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.status, 'rejected')
        self.assertEqual(
            Notification.objects.filter(
                user=self.rolando, tipo='solicitud_denegada',
            ).count(),
            1,
        )

    def test_solo_destinatario_puede_responder(self):
        solicitud = services.crear_solicitud(
            self.rolando, self.pet_rolando, self.pet_jesus,
        )
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(
            reverse('responder_solicitud', args=[solicitud.id, 'aceptar'])
        )
        self.assertEqual(resp.status_code, 404)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.status, 'pending')

    def test_responder_dos_veces_no_duplica_notificaciones(self):
        solicitud = services.crear_solicitud(
            self.rolando, self.pet_rolando, self.pet_jesus,
        )
        self.client.login(username='jesus', password='test1234')
        self.client.post(
            reverse('responder_solicitud', args=[solicitud.id, 'aceptar'])
        )
        self.client.post(
            reverse('responder_solicitud', args=[solicitud.id, 'aceptar'])
        )
        self.assertEqual(
            Notification.objects.filter(
                user=self.rolando, tipo='solicitud_aceptada',
            ).count(),
            1,
        )


class EditPerfilTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando',
            email='rolando@example.com',
            password='test1234',
            nombre='Rolando',
            edad=20,
            ubicacion='Los Teques',
        )

    def test_editar_perfil_get_renderiza_formulario(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('editar_perfil'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Editar Perfil')
        self.assertContains(resp, 'Rolando')

    def test_editar_perfil_post_actualiza_datos(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(reverse('editar_perfil'), {
            'nombre': 'Rolando Actualizado',
            'edad': 25,
            'ubicacion': 'Caracas',
            'descripcion': 'Nueva bio',
        })
        self.assertRedirects(resp, reverse('perfil_usuario'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.nombre, 'Rolando Actualizado')
        self.assertEqual(self.user.edad, 25)
        self.assertEqual(self.user.ubicacion, 'Caracas')

    def test_editar_perfil_post_invalido_no_actualiza(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(reverse('editar_perfil'), {
            'nombre': '',
            'edad': -5,
            'ubicacion': '',
            'descripcion': '',
        })
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nombre, 'Rolando')

    def test_editar_perfil_requiere_login(self):
        resp = self.client.get(reverse('editar_perfil'))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('editar_perfil')}",
        )


class EditPetTests(TestCase):
    def setUp(self):
        self.dueno = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        self.otro = User.objects.create_user(
            username='jesus', email='j@x.com',
            password='test1234', nombre='Jesús',
        )
        self.pet = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.dueno,
        )

    def test_editar_mascota_get_precarga_datos(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('editar_mascota', args=[self.pet.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Editar Mascota')
        self.assertContains(resp, 'Ronaldo')

    def test_editar_mascota_post_actualiza_datos(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(
            reverse('editar_mascota', args=[self.pet.id]),
            {
                'name': 'Ronaldo II',
                'species': 'dog',
                'gender': 'male',
                'age': 6,
                'temperament': 'Tranquilo',
                'description': '',
                'socialization': '',
            },
        )
        self.assertRedirects(resp, reverse('tus_mascotas'))
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, 'Ronaldo II')
        self.assertEqual(self.pet.age, 6)

    def test_editar_mascota_ajena_devuelve_404(self):
        self.client.login(username='jesus', password='test1234')
        resp = self.client.get(reverse('editar_mascota', args=[self.pet.id]))
        self.assertEqual(resp.status_code, 404)

    def test_editar_mascota_requiere_login(self):
        resp = self.client.get(reverse('editar_mascota', args=[self.pet.id]))
        self.assertRedirects(
            resp,
            f"{reverse('login')}?next={reverse('editar_mascota', args=[self.pet.id])}",
        )


def _imagen_png(nombre):
    """Imagen PNG mínima para simular la foto subida de una mascota."""
    buf = io.BytesIO()
    Image.new('RGB', (1, 1), color='red').save(buf, format='PNG')
    return SimpleUploadedFile(nombre, buf.getvalue(), content_type='image/png')


# Tests de la foto actual al editar una mascota
class EditPetFotoTests(TestCase):
    def setUp(self):
        self.dueno = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        self.temp_media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_media, True)
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.pet = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.dueno,
            img=_imagen_png('ronaldo.png'),
        )
        self.client.login(username='rolando', password='test1234')

    def test_editar_mascota_muestra_foto_actual(self):
        resp = self.client.get(reverse('editar_mascota', args=[self.pet.id]))
        self.assertContains(resp, self.pet.img.url)
        self.assertContains(resp, 'Cambiar foto')

    def test_agregar_mascota_no_muestra_foto_actual(self):
        resp = self.client.get(reverse('agregar_mascota'))
        self.assertContains(resp, 'Agregar foto')
        self.assertNotContains(resp, 'Cambiar foto')


# Tests de eliminar mascota
class EliminarMascotaTests(TestCase):
    def setUp(self):
        self.dueno = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        self.otro = User.objects.create_user(
            username='jesus', email='j@x.com',
            password='test1234', nombre='Jesús',
        )
        self.temp_media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_media, True)
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.pet = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.dueno,
            img=_imagen_png('ronaldo.png'),
        )

    def test_eliminar_mascota_propia_la_borra_junto_con_su_foto(self):
        nombre_foto = self.pet.img.name
        storage = self.pet.img.storage
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(
            reverse('eliminar_mascota', args=[self.pet.id]), follow=True,
        )
        self.assertRedirects(resp, reverse('tus_mascotas'))
        self.assertContains(resp, 'Mascota eliminada')
        self.assertFalse(Pet.objects.filter(pk=self.pet.id).exists())
        self.assertFalse(storage.exists(nombre_foto)) #La foto no debe quedar huérfana en media/

    def test_eliminar_mascota_ajena_devuelve_404(self):
        self.client.login(username='jesus', password='test1234')
        resp = self.client.post(reverse('eliminar_mascota', args=[self.pet.id]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Pet.objects.filter(pk=self.pet.id).exists())

    def test_eliminar_mascota_por_get_no_la_borra(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('eliminar_mascota', args=[self.pet.id]))
        self.assertEqual(resp.status_code, 405)
        self.assertTrue(Pet.objects.filter(pk=self.pet.id).exists())

    def test_eliminar_mascota_requiere_login(self):
        url = reverse('eliminar_mascota', args=[self.pet.id])
        resp = self.client.post(url)
        self.assertRedirects(resp, f"{reverse('login')}?next={url}")
        self.assertTrue(Pet.objects.filter(pk=self.pet.id).exists())

    def test_boton_eliminar_solo_aparece_al_editar(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.get(reverse('editar_mascota', args=[self.pet.id]))
        self.assertContains(resp, reverse('eliminar_mascota', args=[self.pet.id]))
        resp = self.client.get(reverse('agregar_mascota'))
        self.assertNotContains(resp, 'Eliminar mascota')


# Pruebas unitarias del servicio de búsqueda (services.buscar_mascotas)
class BuscarMascotasServiceTests(TestCase):
    def setUp(self):
        Pet.objects.create(
            name='Firulais', species='dog', age=3,
            description='Le encanta jugar en el parque',
        )
        Pet.objects.create(
            name='Michi', species='cat', age=2,
            description='Una gata tranquila',
        )
        Pet.objects.create(name='Piolin', species='bird', age=1)

    def _nombres(self, q):
        return [pet.name for pet in services.buscar_mascotas(q)]

    def test_sin_texto_devuelve_todas_ordenadas(self):
        """Sin texto de búsqueda se devuelven todas las mascotas en orden de creación."""
        self.assertEqual(self._nombres(''), ['Firulais', 'Michi', 'Piolin'])

    def test_busca_por_nombre_parcial_sin_importar_mayusculas(self):
        self.assertEqual(self._nombres('FIRU'), ['Firulais'])

    def test_busca_por_especie_en_espanol(self):
        """La especie se guarda en inglés ('cat'), pero el usuario busca «gato»."""
        self.assertEqual(self._nombres('gato'), ['Michi'])
        self.assertEqual(self._nombres('ave'), ['Piolin'])

    def test_busca_por_clave_de_especie(self):
        self.assertEqual(self._nombres('bird'), ['Piolin'])

    def test_busca_por_descripcion(self):
        self.assertEqual(self._nombres('parque'), ['Firulais'])

    def test_sin_coincidencias_devuelve_lista_vacia(self):
        self.assertEqual(self._nombres('ornitorrinco'), [])


# Tests de la pantalla Buscar Mascotas y del buscador del encabezado
class BuscarMascotasTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        Pet.objects.create(
            name='Firulais', species='dog', age=3,
            description='Le encanta jugar en el parque',
        )
        Pet.objects.create(
            name='Michi', species='cat', age=2,
            description='Una gata tranquila',
        )
        self.client.login(username='rolando', password='test1234')

    def test_buscar_por_descripcion(self):
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'parque'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_resultados_muestran_la_descripcion(self):
        resp = self.client.get(reverse('buscar_mascotas'))
        self.assertContains(resp, 'Le encanta jugar en el parque')
        self.assertContains(resp, 'Una gata tranquila')

    def test_pantalla_buscar_tiene_buscador_con_la_busqueda_actual(self):
        #En mobile no hay encabezado, así que la pantalla necesita su propio buscador
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'Michi'})
        self.assertContains(resp, 'id="buscar-q" name="q" type="search" value="Michi"')

    def test_buscador_del_encabezado_lleva_a_buscar_mascotas(self):
        resp = self.client.get(reverse('tus_mascotas'))
        self.assertContains(
            resp,
            f'action="{reverse("buscar_mascotas")}" role="search" class="form-buscar"',
        )

    def test_buscador_del_encabezado_en_el_feed_filtra_el_feed(self):
        resp = self.client.get(reverse('feed'))
        self.assertContains(
            resp,
            f'action="{reverse("feed")}" role="search" class="form-buscar"',
        )

    def test_sin_busqueda_muestra_todas_las_mascotas(self):
        resp = self.client.get(reverse('buscar_mascotas'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Firulais')
        self.assertContains(resp, 'Michi')

    def test_buscar_por_nombre(self):
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'Firulais'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_buscar_por_especie_en_espanol(self):
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'perro'})
        self.assertContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_resultados_enlazan_al_perfil_de_cada_mascota(self):
        resp = self.client.get(reverse('buscar_mascotas'))
        for pet in Pet.objects.all():
            self.assertContains(resp, f'href="{reverse("ver_mascota", args=[pet.id])}"')

    def test_buscar_requiere_iniciar_sesion(self):
        self.client.logout()
        url = reverse('buscar_mascotas')
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('login')}?next={url}")

    def test_sin_resultados_muestra_mensaje(self):
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'ornitorrinco'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sin resultados para esa búsqueda.')
        self.assertNotContains(resp, 'Firulais')
        self.assertNotContains(resp, 'Michi')

    def test_busqueda_ignora_espacios_alrededor(self):
        resp = self.client.get(reverse('buscar_mascotas'), {'q': '   Michi   '})
        self.assertContains(resp, 'Michi')
        self.assertNotContains(resp, 'Firulais')
        self.assertContains(resp, 'value="Michi"')

    def test_boton_limpiar_solo_aparece_con_busqueda(self):
        resp = self.client.get(reverse('buscar_mascotas'))
        self.assertNotContains(resp, 'class="buscar-limpiar"')
        resp = self.client.get(reverse('buscar_mascotas'), {'q': 'Michi'})
        self.assertContains(resp, 'class="buscar-limpiar"')

    def test_texto_buscado_se_escapa_en_la_pagina(self):
        """Seguridad: lo que escribe el usuario no debe ejecutarse como HTML (XSS)."""
        resp = self.client.get(reverse('buscar_mascotas'), {'q': '<script>alert(1)</script>'})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, '<script>alert(1)</script>')
        self.assertContains(resp, '&lt;script&gt;alert(1)&lt;/script&gt;')


# Tests del mini popup de confirmación al enviar una solicitud
class ConfirmacionSolicitudTests(TestCase):
    def setUp(self):
        self.rolando = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        self.jesus = User.objects.create_user(
            username='jesus', email='j@x.com',
            password='test1234', nombre='Jesús',
        )
        self.pet_rolando = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.rolando,
        )
        self.pet_jesus = Pet.objects.create(
            name='Brown', species='dog', age=1, owner=self.jesus,
        )

    def test_solicitud_enviada_se_muestra_en_mini_popup(self):
        self.client.login(username='rolando', password='test1234')
        resp = self.client.post(
            reverse('enviar_solicitud', args=[self.pet_jesus.id]),
            {'from_pet': self.pet_rolando.id},
            follow=True,
        )
        self.assertRedirects(resp, reverse('ver_mascota', args=[self.pet_jesus.id]))
        self.assertContains(resp, 'notif-toast--esquina')
        self.assertContains(resp, 'Solicitud enviada')


class MensajesTests(TestCase):
    def setUp(self):
        self.rolando = User.objects.create_user(
            username='rolando', email='r@x.com',
            password='test1234', nombre='Rolando',
        )
        self.jesus = User.objects.create_user(
            username='jesus', email='j@x.com',
            password='test1234', nombre='Jesús',
        )
        self.pet_rolando = Pet.objects.create(
            name='Ronaldo', species='dog', age=5, owner=self.rolando,
        )
        self.pet_jesus = Pet.objects.create(
            name='Brown', species='dog', age=1, owner=self.jesus,
        )
        FriendshipRequest.objects.create(
            from_user=self.jesus, to_user=self.rolando,
            from_pet=self.pet_jesus, to_pet=self.pet_rolando,
            status='accepted',
        )
        self.client.force_login(self.rolando)

    def _notificaciones_de_jesus(self):
        return Notification.objects.filter(user=self.rolando, tipo='mensaje', from_user=self.jesus)

    def test_abrir_el_chat_marca_la_notificacion_como_leida(self):
        services.enviar_mensaje(self.jesus, self.rolando, 'Hola')
        self.client.get(reverse('ver_conversacion', args=[self.jesus.id]))
        self.assertFalse(self._notificaciones_de_jesus().filter(leida=False).exists())

    def test_mensaje_nuevo_despues_de_leer_vuelve_a_notificar(self):
        services.enviar_mensaje(self.jesus, self.rolando, 'Hola')
        self.client.get(reverse('ver_conversacion', args=[self.jesus.id]))
        services.enviar_mensaje(self.jesus, self.rolando, '¿Vamos al parque?')
        self.assertEqual(self._notificaciones_de_jesus().count(), 2)
        self.assertEqual(self._notificaciones_de_jesus().filter(leida=False).count(), 1)

    def test_no_se_puede_chatear_sin_solicitud_aceptada(self):
        carla = User.objects.create_user(username='carla', password='test1234')
        resp = self.client.get(reverse('ver_conversacion', args=[carla.id]))
        self.assertRedirects(resp, reverse('bandeja_entrada'))

    def test_flecha_del_chat_vuelve_a_la_bandeja(self):
        resp = self.client.get(reverse('ver_conversacion', args=[self.jesus.id]))
        self.assertContains(resp, f'href="{reverse("bandeja_entrada")}" class="chat-atras"')

    def test_la_cabecera_tiene_acceso_a_mensajes(self):
        resp = self.client.get(reverse('perfil_usuario'))
        self.assertContains(resp, f'<a href="{reverse("bandeja_entrada")}"><img id="icono-chat"')

    def test_la_barra_de_ver_mascota_lleva_a_la_bandeja(self):
        resp = self.client.get(reverse('ver_mascota', args=[self.pet_jesus.id]))
        self.assertNotContains(resp, '<a href="#">')
        self.assertContains(resp, f'href="{reverse("bandeja_entrada")}"')


class PopupNotificacionesTests(TestCase):
    def setUp(self):
        self.rolando = User.objects.create_user(username='rolando', password='test1234')
        self.jesus = User.objects.create_user(username='jesus', password='test1234')
        self.pet_rolando = Pet.objects.create(name='Ronaldo', species='dog', age=5, owner=self.rolando)
        self.pet_jesus = Pet.objects.create(name='Brown', species='dog', age=1, owner=self.jesus)
        self.client.force_login(self.rolando)

    def test_notificacion_de_mensaje_abre_el_chat(self):
        services.enviar_mensaje(self.jesus, self.rolando, 'Hola')
        resp = self.client.get(reverse('perfil_usuario'))
        chat = reverse('ver_conversacion', args=[self.jesus.id])
        self.assertContains(resp, f'class="notif-popup-enlace" href="{chat}"')

    def test_notificacion_de_solicitud_lleva_a_notificaciones(self):
        services.crear_solicitud(self.jesus, self.pet_jesus, self.pet_rolando)
        resp = self.client.get(reverse('perfil_usuario'))
        self.assertContains(resp, f'class="notif-popup-enlace" href="{reverse("notificaciones")}"')


class AgregarMascotaNavegacionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rolando', password='test1234')
        self.client.force_login(self.user)

    def test_buscador_lleva_a_buscar_mascotas(self):
        resp = self.client.get(reverse('agregar_mascota'))
        self.assertContains(resp, f'action="{reverse("buscar_mascotas")}" role="search"')

    def test_iconos_llevan_a_su_pantalla(self):
        resp = self.client.get(reverse('agregar_mascota'))
        for nombre in ('perfil_usuario', 'bandeja_entrada', 'notificaciones', 'feed'):
            self.assertContains(resp, f'href="{reverse(nombre)}"')
        self.assertContains(resp, f'action="{reverse("logout")}"')
