from django.urls import path
from .views import *

app_name = 'app'
urlpatterns = [
    # client views
    path("turnos/", TipoTicketListView.as_view(), name="select_tipo"),
    path("turnos/new/", TicketCreateView.as_view(), name="create_ticket"),
    path("turnos/detail/", TicketDetailView.as_view(), name="detail"), # no used
    
]