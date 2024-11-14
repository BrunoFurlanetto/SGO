from django.urls import path

from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_relatorio_cozinha, name='cadastro_relatorio_cozinha'),
    path('cadastro/salvar_evento/', views.salvar_evento, name='salvar_evento'),
]
