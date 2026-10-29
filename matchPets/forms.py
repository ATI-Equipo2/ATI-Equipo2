from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Pet, User


class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'nombre']
        labels = {
            'username': _('Usuario'),
            'email': _('Correo'),
            'nombre': _('Nombre'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = _('Contraseña')
        self.fields['password2'].label = _('Confirmar contraseña')
        self.fields['email'].required = True
        self.fields['nombre'].required = True
        # Los estilos de .field-group aplican a los inputs; solo se ajustan atributos.
        atributos = {
            'username': {'placeholder': _('Usuario'), 'autocomplete': 'username'},
            'email': {'placeholder': _('ej: nombre@gmail.com'), 'autocomplete': 'email'},
            'nombre': {'placeholder': _('Nombre'), 'autocomplete': 'given-name'},
            'password1': {'placeholder': '**********', 'autocomplete': 'new-password'},
            'password2': {'placeholder': '**********', 'autocomplete': 'new-password'},
        }
        for campo, attrs in atributos.items():
            self.fields[campo].widget.attrs.update(attrs)


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name', 'species', 'gender', 'age', 'temperament', 'description', 'socialization', 'img']
        labels = {
            'name': _('Nombre'),
            'species': _('Especie'),
            'age': _('Edad'),
            'description': _('Descripción'),
            'temperament': _('Temperamento'),
            'socialization': _('En busca de socializar'),
            'gender': _('Sexo'),
            'img': _('Foto'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Nombre'), 'autocomplete': 'off'}),
            'age': forms.NumberInput(attrs={'placeholder': _('Edad en años'), 'min': 0}),
            'temperament': forms.TextInput(attrs={'placeholder': _('ej: alegre'), 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'placeholder': _('Cuéntanos sobre tu mascota'), 'rows': 3}),
            'socialization': forms.Textarea(attrs={'placeholder': _('ej: busca un compañero para jugar en el parque'), 'rows': 3}),
            'img': forms.FileInput(attrs={
                'id': 'pet-photo',
                'accept': 'image/*',
                'style': 'display: none;',
                'onchange': "if(this.files[0]) document.getElementById('photo-label-text').textContent = this.files[0].name;",
            }),
        }

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 0:
            raise forms.ValidationError(_('La edad no puede ser negativa.'))
        return age

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nombre', 'edad', 'ubicacion', 'descripcion', 'foto']
        labels = {
            'nombre': _('Nombre'),
            'edad': _('Edad'),
            'ubicacion': _('Ubicación'),
            'descripcion': _('Descripción'),
            'foto': _('Foto de perfil'),
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': _('Nombre'), 'autocomplete': 'given-name'}),
            'edad': forms.NumberInput(attrs={'placeholder': _('Edad'), 'min': 0}),
            'ubicacion': forms.TextInput(attrs={'placeholder': _('Ubicación'), 'autocomplete': 'address-level2'}),
            'descripcion': forms.Textarea(attrs={'placeholder': _('Cuéntanos sobre ti'), 'rows': 4}),
        }

    def clean_edad(self):
        edad = self.cleaned_data.get('edad')
        if edad is not None and edad < 0:
            raise forms.ValidationError(_('La edad no puede ser negativa.'))
        return edad