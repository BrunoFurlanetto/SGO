from django.urls import path

from . import views

urlpatterns = [
    path('', views.novo_orcamento, name='novo_orcamento'),
    path('tratativa/<str:id_tratativa>/', views.clonar_orcamento, name='clonar_orcamento'),
    path('calculos/', views.calc_budget, name='calculos_orcamento'),
    path('preencher_op_extras/', views.preencher_op_extras, name='preencher_op_extras'),
    path('preencher_orcaento_promocional/', views.preencher_orcamento_promocional, name='preencher_orcaento_promocional'),
    path('validar_produtos/', views.validar_produtos, name='validar_produtos'),
    path('verificar_responsaveis/', views.verificar_responsaveis, name='verificar_responsaveis'),
    path('pesquisar_op/', views.pesquisar_op, name='pesquisar_op'),
    path('pegar_dados_pacoe/', views.pegar_dados_pacoe, name='pegar_dados_pacoe'),
    path('salvar_pacote/', views.salvar_pacote, name='salvar_pacote'),
    path('verificar_gerencia/', views.veriricar_gerencia, name='verificar_gerencia'),
    path('pdf_orcamento/<str:id_tratativa>', views.gerar_pdf, name='pdf_orcamento'),
]
