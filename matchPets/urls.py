from django.urls import path
from .views import login, signup, add_pet, base_navigation, base_feed_mobile, base_perfil
from .views import perfil_usuario, ver_dueno, perfil_mascota, ver_mascota, tus_mascotas, sus_mascotas

urlpatterns = [
    path('', signup, name='registro'),
    path('inicio_sesion/', login, name='inicio_sesion'),
    path('agregar_mascota/', add_pet, name='agregar_mascota'),
    path('base_navegacion/', base_navigation, name='base_navegacion'),
    path('base_feed_mobile/', base_feed_mobile, name='base_feed_mobile'),
    path('base_perfil/', base_perfil, name='base_perfil'),
    path('perfil_usuario/', perfil_usuario, name='perfil_usuario'),
    path('ver_dueno/', ver_dueno, name='ver_dueno'),
    path('perfil_mascota/', perfil_mascota, name='perfil_mascota'),
    path('ver_mascota/', ver_mascota, name='ver_mascota'),
    path('tus_mascotas/', tus_mascotas, name='tus_mascotas'),
    path('sus_mascotas/', sus_mascotas, name='sus_mascotas')
]
