from django.shortcuts import render

from django.http import HttpResponse

def hello_world(request):
    return HttpResponse("¡Hola Mundo desde Django!")

def hola_mundo(request):
    return render(request, 'index.html')

def inicio(request):
    return render(request, 'index.html', {'nombre': 'Registrarse'})

def inicio_sesion(request):
    return render(request, 'index.html', {'nombre': 'Iniciar Sesión'})

def agregar_mascota(request):
    return render(request, 'index.html', {'nombre': 'Agregar Mascota'})

def base_navegacion(request):
    return render(request, 'base-navegacion-desktop.html')

def base_feed_mobile(request):
    return render(request, 'base-feed-mobile.html')

def base_perfil(request):
    return render(request, 'base-perfil.html')