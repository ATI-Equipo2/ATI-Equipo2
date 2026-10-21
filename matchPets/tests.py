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


#PNG mínimo para probar las fotos
PNG_MINIMO = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00'
    b'\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

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
        imagen = SimpleUploadedFile(
            'firulais.png',
            PNG_MINIMO,
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
