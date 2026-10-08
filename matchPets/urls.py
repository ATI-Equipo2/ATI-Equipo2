from django.urls import path
from .views import inicio, inicio_sesion, agregar_mascota, base_navegacion, base_feed_mobile, base_perfil

urlpatterns = [
    path('', inicio, name='inicio'),
    path('inicio_sesion/', inicio_sesion, name='inicio_sesion'),
    path('agregar_mascota/', agregar_mascota, name='agregar_mascota'),
    path('base_navegacion/', base_navegacion, name='base_navegacion'),
    path('base_feed_mobile/', base_feed_mobile, name='base_feed_mobile'),
    path('base_perfil/', base_perfil, name='base_perfil')
]

