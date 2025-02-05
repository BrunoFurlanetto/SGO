from django.urls import path

from . import views

urlpatterns = [
    path('encontrar_chat/orcamento/', views.encontrar_chat_orcamento, name='econtrar_chat_orcamento'),
    path('orcamento/salvar/', views.salvar_mensagem, name='salvar_mensagem'),
]
