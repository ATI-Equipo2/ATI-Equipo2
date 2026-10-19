from django.test import TestCase
from django.contrib.auth import get_user_model
from matchPets.models import Pet
from matchPets.forms import RegistroForm

User = get_user_model()


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