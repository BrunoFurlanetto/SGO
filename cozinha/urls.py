from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard_cozinha'),
    path('verificar_relatorios_dia/<str:data>/', views.verificar_relatorios_dia, name='verificar_relatorios_dia'),
    path('cadastro/', views.cadastro_relatorio_evento_cozinha, name='cadastro_relatorio_cozinha'),
    path('cadastro/salvar_evento/', views.salvar_evento, name='salvar_evento'),
    path('cadastro/relatorio/dia/', views.cadastro_relatorio_dia_cozinha, name='cadastro_relatorio_dia_cozinha'),
    path('edicao/relatorio/dia/<str:data_edicao>/', views.edicao_relatorio_dia_cozinha, name='edicao_relatorio_dia_cozinha'),
    path('edicao/relatorio/evento/<int:id_relatorio>/', views.edicao_relatorio_evento_cozinha, name='edicao_relatorio_evento_cozinha'),
    path('cadastro/relatorio/dia/<str:data_refeicoes>/salvar/', views.salvar_relatorio_dia, name='salvar_relatorio_dia'),
]
