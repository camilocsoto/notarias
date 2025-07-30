from django import forms
from django.contrib.auth.forms import AuthenticationForm

class AuthForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.TextInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error si es necesario
        self.fields["username"].label = "Correo electrónico"
        self.fields["password"].label = "Contraseña"