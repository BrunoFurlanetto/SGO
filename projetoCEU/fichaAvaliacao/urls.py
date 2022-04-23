from django.urls import path
from . import views

urlpatterns = [
    path('', views.fichaAvaliacao, name='fichaAvaliacao'),
    path('agradecimento/', views.agradecimentos, name='agradecimentos'),
]
