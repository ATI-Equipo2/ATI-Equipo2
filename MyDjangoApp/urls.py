from django.urls import path
from . import views

urlpatterns = [
# Esta será la página de inicio de la aplicación
path('', views.post_list, name='post_list'),
]
