from django.urls import path

from . import views

urlpatterns = [
    path('', views.novo_orcamento, name='novo_orcamento'),
    path('tratativa/<str:id_tratativa>/', views.clonar_orcamento, name='clonar_orcamento'),
    path('calculos/', views.calc_budget, name='calculos_orcamento'),
    path('salvar/', views.salvar_orcamento, name='salvar_orcamento'),
    path('salvar/<str:id_tratativa>/', views.salvar_orcamento, name='salvar_orcamento_clone'),
    path('editar_previa/<int:id_orcamento>/', views.editar_previa, name='editar_previa'),
    path('apagar/<int:id_orcamento>/', views.apagar_orcamento, name='apagar_orcamento'),
    path('preencher_op_extras/', views.preencher_op_extras, name='preencher_op_extras'),
    path('preencher_orcamento_promocional/', views.preencher_orcamento_promocional, name='preencher_orcamento_promocional'),
    path('verificar_pacotes_promocionais/', views.verificar_pacotes_promocionais, name='verificar_pacotes_promocionais'),
    path('editar_pacotes_promocionais/<int:id_dados_pacote>', views.editar_pacotes_promocionais, name='editar_pacotes_promocionais'),
    path('validar_produtos/', views.validar_produtos, name='validar_produtos'),
    path('verificar_responsaveis/', views.verificar_responsaveis, name='verificar_responsaveis'),
    path('pesquisar_op/', views.pesquisar_op, name='pesquisar_op'),
    path('pegar_dados_pacote/', views.pegar_dados_pacote, name='pegar_dados_pacote'),
    path('salvar_pacote/', views.salvar_pacote, name='salvar_pacote'),
    path('verificar_gerencia/', views.veriricar_gerencia, name='verificar_gerencia'),
    path('pdf_orcamento/<str:id_tratativa>/', views.gerar_pdf, name='pdf_orcamento'),
    path('previa_pdf_orcamento/<int:id_orcamento>/', views.gerar_pdf_previa, name='previa_pdf_orcamento'),
    path('pegar_orcamentos_tratativa/', views.pegar_orcamentos_tratativa, name='pegar_orcamentos_tratativa'),
    path('verificar_validade_op/', views.verificar_validade_opcionais, name='verificar_validade_opcionais'),
    path('aprovacao_gerencia/<int:id_orcamento>/<int:gerente_aprovando>', views.editar_previa, name='aprovacao_gerencia'),
]
