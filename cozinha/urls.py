from django.urls import path

from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_relatorio_evento_cozinha, name='cadastro_relatorio_cozinha'),
    path('cadastro/salvar_evento/', views.salvar_evento, name='salvar_evento'),
    path('cadastro/relatorio/dia/', views.cadastro_relatorio_dia_cozinha, name='cadastro_relatorio_dia_cozinha'),
    path('cadastro/relatorio/dia/<str:data>/salvar/', views.salvar_relatorio_dia, name='salvar_relatorio_dia'),
]
