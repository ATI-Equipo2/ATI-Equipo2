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
        fields = ['name', 'species', 'age', 'description', 'gender', 'img']
        labels = {
            'name': _('Nombre'),
            'species': _('Especie'),
            'age': _('Edad'),
            'description': _('Descripción'),
            'gender': _('Sexo'),
            'img': _('Foto'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Nombre'), 'autocomplete': 'off'}),
            'age': forms.NumberInput(attrs={'placeholder': _('Edad en años'), 'min': 0}),
            'description': forms.Textarea(attrs={'placeholder': _('ej: alegre y juguetón'), 'rows': 3}),
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
