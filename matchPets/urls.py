from django.urls import path
from .views import login, signup, agregar_mascota, base_navegacion, base_feed_mobile, base_perfil

urlpatterns = [
    path('', signup, name='registro'),
    path('inicio_sesion/', login, name='inicio_sesion'),
    path('agregar_mascota/', agregar_mascota, name='agregar_mascota'),
    path('base_navegacion/', base_navegacion, name='base_navegacion'),
    path('base_feed_mobile/', base_feed_mobile, name='base_feed_mobile'),
    path('base_perfil/', base_perfil, name='base_perfil')
]

