from django.urls import path
from .views import login, signup, add_pet, base_navigation, base_feed_mobile, base_perfil

urlpatterns = [
    path('', signup, name='registro'),
    path('inicio_sesion/', login, name='inicio_sesion'),
    path('agregar_mascota/', add_pet, name='agregar_mascota'),
    path('base_navegacion/', base_navigation, name='base_navegacion'),
    path('base_feed_mobile/', base_feed_mobile, name='base_feed_mobile'),
    path('base_perfil/', base_perfil, name='base_perfil')
]
