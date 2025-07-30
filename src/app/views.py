from django.urls import reverse
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Ticket, TipoTicket
from accounts.models import User
from typing import cast

class TipoTicketListView(LoginRequiredMixin, ListView):
    model = TipoTicket
    template_name = "client/kiosko.html"
    context_object_name = "tipos"

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = []                # no exponemos campos
    http_method_names = ['post']
    template_name = "client/detail.html"  # template para mostrar el resultado

    def post(self, request, *args, **kwargs):
        # 1) Obtener tipo y generar número
        tipo_id = request.POST.get('tipo_id')
        tipo = TipoTicket.objects.get(pk=tipo_id)
        tipo.ultimo_numero += 1
        tipo.save()
        numero = f"{tipo.letra}-{tipo.ultimo_numero:03d}"

        # 2) Crear el ticket y guardarlo en self.object
        user = cast(User, request.user)
        ticket = Ticket.objects.create(
            numero_turno=numero,
            tipo_servicio=tipo,
            cliente=user,
            notaria=user.notaria,
        )
        self.object = ticket   # ← importante

        # 3) Renderizar el detalle usando el mismo context name que espera CreateView
        context = self.get_context_data(ticket=ticket)
        return self.render_to_response(context)


class TicketDetailView(LoginRequiredMixin, TemplateView):
    template_name = "client/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # suponemos que la vista recibe 'ticket' en context
        ctx['ticket'] = kwargs.get('ticket')
        return ctx
    
