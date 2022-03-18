from django.urls import path
from . import views

urlpatterns = [
    path('publico/', views.publico, name='publico'),
    path('colegio/', views.colegio, name='colegio'),
    path('empresa/', views.empresa, name='empresa'),
    path('ordem_de_servico/', views.ordemDeServico, name='ordem_de_servico'),
    path('ficha_de_evento/', views.fichaDeEvento, name='ficha_de_evento'),
]
