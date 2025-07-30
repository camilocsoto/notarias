from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from app.models import Ticket, TipoTicket
from accounts.models import User
from app.forms import TicketUpdateForm
from typing import cast

# views for the client

class TipoTicketListView(LoginRequiredMixin, ListView):
    model = TipoTicket
    template_name = "client/kiosko.html"
    context_object_name = "tipos"

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = []
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
        self.object = ticket

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
    
# views for the boxman

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'operator/ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        user = cast(User, self.request.user)
        # Aseguramos que user.notaria no sea None
        assert user.notaria is not None, "El usuario debe pertenecer a una notaría"
        return (
            Ticket.objects
            .filter(notaria=user.notaria)
            .exclude(estado__in=['cancelado', 'finalizado'])
            .order_by('fecha_creacion')
        )

    def get_context_data(self, **kwargs):
        user = cast(User, self.request.user)
        # Pylance ahora sabe user.notaria no es None
        assert user.notaria is not None, "El usuario debe tener asignada una notaría"
        ctx = super().get_context_data(**kwargs)
        ctx['usuario'] = user.get_full_name() or user.username
        ctx['notaria'] = user.notaria.nombre
        return ctx

class TicketAttendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = cast(User, request.user)
        assert user.notaria is not None, "El usuario debe pertenecer a una notaría"
        ticket = get_object_or_404(
            Ticket,
            pk=pk,
            notaria=user.notaria
        )
        ticket.estado = 'llamado'
        ticket.fecha_atencion = timezone.now()
        ticket.operador = user
        ticket.save()
        return redirect('app:ticket_update', pk=pk)

class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketUpdateForm
    template_name = 'operator/ticket_update.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        user = cast(User, self.request.user)
        assert user.notaria is not None, "El usuario debe pertenecer a una notaría"
        return super().get_queryset().filter(notaria=user.notaria)

    def form_valid(self, form):
        user = cast(User, self.request.user)
        ticket = form.save(commit=False)
        ticket.operador = user
        ticket.save()
        return redirect('app:ticket_list')
    
    # TV show
    
class TicketTVListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'client/tv.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        user = cast(User, self.request.user)
        assert user.notaria is not None, "Usuario sin notaría asignada"
        # Excluimos finalizado/cancelado y ordenamos por creación ascendente
        return (
            Ticket.objects
            .filter(notaria=user.notaria)
            .exclude(estado__in=['finalizado', 'cancelado'])
            .order_by('fecha_creacion')
        )

    def get_context_data(self, **kwargs):
        user = cast(User, self.request.user)
        assert user.notaria is not None, "Usuario sin notaría asignada"
        ctx = super().get_context_data(**kwargs)
        ctx['notaria'] = user.notaria.nombre
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('ajax') == '1':
            # Usamos la función render_to_string, no self.render_to_string
            html = render_to_string(
                'client/partials/tv_table_body.html',
                context,
                request=self.request
            )
            return HttpResponse(html, content_type='text/html')
        return super().render_to_response(context, **response_kwargs)