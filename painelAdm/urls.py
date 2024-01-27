from django.urls import path
from . import views

urlpatterns = [
    path('resumo_atividades/', views.resumo_ceu, name='resumo_atividades'),
    path('', views.painelGeral, name='painelGeral')
]
