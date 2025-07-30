from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import User
from app.models import Notaria

class UserForm(UserCreationForm):
    
    first_name = forms.CharField(
        label="Nombre(s)",
        max_length=150,
        required=True
    )
    last_name = forms.CharField(
        label="Apellido(s)",
        max_length=150,
        required=True
    )
    
    # Campo de rol usando las mismas opciones que el modelo
    rol = forms.ChoiceField(
        label="Rol",
        choices=User.ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    # Campo de notaría con queryset dinámico
    notaria = forms.ModelChoiceField(
        label="Notaría",
        queryset=Notaria.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,  # Porque el modelo permite null
        empty_label="-- Seleccione una notaría --"
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        required=True
    )
    
    class Meta():
        model = User
        fields = ['first_name', 'last_name', 'email', 'rol', 'notaria','password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets y atributos si es necesario
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Opcional: filtrar notarías según el contexto
        # Por ejemplo, si solo quieres notarías activas:
        # self.fields['notaria'].queryset = Notaria.objects.filter(isActive=True)
    
    def clean_email(self):
        """Validar que el email sea único para el username."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email
    
    def save(self, commit=True):
        """Guardar el usuario con el username igual al email."""
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        
        # El rol ya se asigna automáticamente desde el formulario
        
        if commit:
            user.save()
        return user