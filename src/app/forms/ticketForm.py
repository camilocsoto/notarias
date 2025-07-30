from django import forms
from app.models import Ticket

class TicketUpdateForm(forms.ModelForm):
    estado = forms.ChoiceField(
        choices=Ticket.ESTADO_CHOICES,
        widget=forms.RadioSelect,
        label="Estado"
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label="Comentarios"
    )

    class Meta:
        model = Ticket
        fields = ['comments', 'estado']