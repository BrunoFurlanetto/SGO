from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard_cozinha'),
    # path('verificar_relatorios_dia/<str:data>/', views.verificar_relatorios_dia, name='verificar_relatorios_dia'),
    # path('cadastro/', views.cadastro_relatorio_evento_cozinha, name='cadastro_relatorio_cozinha'),
    # path('cadastro/salvar_evento/', views.salvar_evento, name='salvar_evento'),
    # path('cadastro/relatorio/dia/', views.cadastro_relatorio_dia_cozinha, name='cadastro_relatorio_dia_cozinha'),
    path('visualizar/relatorio/dia/<str:data>/', views.ver_relatorio_dia_cozinha, name='visualizar_relatorio_dia_cozinha'),
    path('visualizar/relatorio/evento/<int:id_evento>/', views.ver_relatorio_evento_cozinha, name='visualizar_relatorio_evento_cozinha'),
    path('salvar/visualizacao/', views.salvar_visualizacao_cozinheiro, name='salvar_visualizacao_cozinheiro'),
    # path('cadastro/relatorio/dia/<str:data_refeicoes>/salvar/', views.salvar_relatorio_dia, name='salvar_relatorio_dia'),
]
