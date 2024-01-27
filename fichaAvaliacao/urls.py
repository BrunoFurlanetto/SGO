from django.urls import path
from . import views

urlpatterns = [
    path('', views.fichaAvaliacao, name='fichaAvaliacao'),
    path('<int:id_ficha>/', views.fichaAvaliacao, name='verFichaAvaliacao'),
    path('agradecimento/', views.agradecimentos, name='agradecimentos'),
    path('entregues/', views.entregues, name='entregues'),
]
