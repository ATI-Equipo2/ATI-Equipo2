from django.test import TestCase
from django.contrib.auth import get_user_model
from matchPets.models import Pet

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