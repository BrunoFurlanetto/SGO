from django.urls import path
from . import views

urlpatterns = [
    path('', views.fichaAvaliacao, name='fichaAvaliacao'),
    path('agradecimento/', views.agradecimentos, name='agradecimentos'),
    path('entregues/', views.entregues, name='entregues'),
    path('<int:id_fichaDeAvaliacao>/', views.verFicha, name='verFichaAvaliacao'),
]
