from django.urls import path
from . import views

urlpatterns = [
    path('publico/', views.publico, name='publico'),
    path('colegio/', views.colegio, name='colegio'),
    path('empresa/', views.empresa, name='empresa'),
    path('ordem_de_servico/', views.ordemDeServico, name='ordem_de_servico'),
    path('ordem_de_servico/<int:id_ordem_de_servico>', views.ordemDeServico, name='ver_ordem_de_servico'),
    path('ordem_de_servico/ficha/<int:id_ficha_de_evento>', views.ordemDeServico, name='ordem_de_servico_com_ficha'),
    path('ficha_de_evento/', views.fichaDeEvento, name='ficha_de_evento'),
    path('ficha_de_evento/<int:id_pre_reserva>', views.fichaDeEvento, name='ficha_de_evento'),
    path('ficha_de_evento/visualizar/<int:id_ficha_de_evento>', views.fichaDeEvento, name='ver_ficha_de_evento'),
    path('lista_cliente/', views.listaCliente, name='lista_cliente'),
    path('lista_responsaveis/', views.listaResponsaveis, name='lista_responsaveis'),
]
