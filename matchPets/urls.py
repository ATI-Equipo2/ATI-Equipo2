from django.urls import path
from .views import signup, add_pet, base_navigation, base_feed_mobile, base_perfil
from .views import perfil_usuario, ver_dueno, perfil_mascota, ver_mascota, tus_mascotas, sus_mascotas
from .views import notificaciones, buscar_mascotas
from .views import enviar_solicitud, responder_solicitud, marcar_leida, descartar_notificacion
from .views import feed, inicio
from .views import LoginView, LogoutView, vista_protegida

urlpatterns = [
    path('', signup, name='registro'),
    path('signup/', signup, name='signup'),
    path('agregar_mascota/', add_pet, name='agregar_mascota'),
    path('base_navegacion/', base_navigation, name='base_navegacion'),
    path('base_feed_mobile/', base_feed_mobile, name='base_feed_mobile'),
    path('base_perfil/', base_perfil, name='base_perfil'),
    path('perfil_usuario/', perfil_usuario, name='perfil_usuario'),
    path('ver_dueno/<int:user_id>/', ver_dueno, name='ver_dueno'),
    path('perfil_mascota/<int:pet_id>/', perfil_mascota, name='perfil_mascota'),
    path('ver_mascota/<int:pet_id>/', ver_mascota, name='ver_mascota'),
    path('tus_mascotas/', tus_mascotas, name='tus_mascotas'),
    path('sus_mascotas/<int:user_id>/', sus_mascotas, name='sus_mascotas'),
    path('notificaciones/', notificaciones, name='notificaciones'),
    path('notificaciones/<int:notif_id>/leida/', marcar_leida, name='marcar_leida'),
    path('notificaciones/<int:notif_id>/descartar/', descartar_notificacion, name='descartar_notificacion'),
    path('ver_mascota/<int:pet_id>/solicitud/', enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes/<int:req_id>/<slug:accion>/', responder_solicitud, name='responder_solicitud'),
    path('buscar_mascotas/', buscar_mascotas, name='buscar_mascotas'),
    path('inicio/', inicio, name='inicio'),
    path('feed/', feed, name='feed'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protegida/', vista_protegida, name='vista_protegida'),
]
