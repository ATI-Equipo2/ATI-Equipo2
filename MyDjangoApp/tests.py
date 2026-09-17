from django.test import TestCase

class PruebasSencillas(TestCase):
    def test_matematica_basica(self):
        self.assertEqual(2 + 2, 4)

    def test_servidor_responde(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)