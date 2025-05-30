from django.urls import path
from . import views

urlpatterns = [
    path('publico/', views.publico, name='publico'),
    path('relatorio/publico/<int:id_relatorio>', views.publico, name='editar_publico'),
    path('colegio/', views.colegio, name='colegio'),
    path('relatorio/colegio/<int:id_relatorio>', views.colegio, name='editar_colegio'),
    path('relatorio/colegio/ordem_servico/<int:id_ordem>', views.relatorio_colegio, name='cadastro_relatorio_colegio'),
    path('empresa/', views.empresa, name='empresa'),
    path('relatorio/empresa/ordem_servico/<int:id_ordem>', views.cadastro_relatorio_empresa, name='cadastro_relatorio_empresa'),
    path('relatorio/empresa/<int:id_relatorio>', views.empresa, name='editar_empresa'),
    path('ordem_de_servico/', views.inicioOrdemDeServico, name='ordem_de_servico'),
    path('ordem_de_servico/<int:id_ordem_de_servico>', views.ordemDeServico, name='ver_ordem_de_servico'),
    path('ordem_de_servico/salvar', views.ordemDeServico, name='salvar_ordem_de_servico'),
    path('ordem_de_servico/ficha/<int:id_ficha_de_evento>', views.ordemDeServico, name='ordem_de_servico_com_ficha'),
    path('ficha_de_evento/', views.fichaDeEvento, name='ficha_de_evento'),
    path('ficha_de_evento/<int:id_pre_reserva>', views.fichaDeEvento, name='ficha_de_evento'),
    path('ficha_de_evento/visualizar/<int:id_ficha_de_evento>', views.fichaDeEvento, name='ver_ficha_de_evento'),
    path('lista_cliente/', views.listaCliente, name='lista_cliente'),
    path('lista_responsaveis/', views.listaResponsaveis, name='lista_responsaveis'),
]
