from django.urls import path
from . import views

urlpatterns = [
    path('', views.fichaAvaliacao, name='fichaAvaliacao'),
    path('solicitacao/', views.solicitarFichaAvaliacao, name='solicitarAvaliacao'),
]
