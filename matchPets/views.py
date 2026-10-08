from django.shortcuts import render

from django.http import HttpResponse

def signup(request):
    return render(request, 'signup.html', {'name': 'Registrarse'})

def login(request):
    return render(request, 'login.html', {'name': 'Iniciar Sesión'})

def add_pet(request):
    return render(request, 'add-pet.html', {'name': 'Agregar Mascota'})

def base_navigation(request):
    return render(request, 'base-navigation-desktop.html')

def base_feed_mobile(request):
    return render(request, 'base-feed-mobile.html')

def base_perfil(request):
    return render(request, 'base-perfil.html')
