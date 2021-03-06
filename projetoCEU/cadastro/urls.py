from django.urls import path
from . import views

urlpatterns = [
    path('publico/', views.publico, name='publico'),
    path('colegio/', views.colegio, name='colegio'),
    path('empresa/', views.empresa, name='empresa'),
    path('ordem_de_servico/', views.ordemDeServico, name='ordem_de_servico'),
    path('ficha_de_evento/', views.fichaDeEvento, name='ficha_de_evento'),
    path('ficha_de_evento/<int:id_cliente>', views.fichaDeEvento, name='ficha_de_evento'),
    path('lista_cliente/', views.listaCliente, name='lista_cliente'),
    path('lista_responsaveis/', views.listaResponsaveis, name='lista_responsaveis'),
]
