from django.contrib import admin
from matchPets.models import Pet
from .models import User

admin.site.register(User)

# Register your models here.
admin.site.register(Pet)  # para poder ver las mascotas desde admin
