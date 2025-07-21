from django.urls import path
from . import views

urlpatterns = [
    path('evento/<int:id_ordem>', views.cadastrar_nova_ficha, name='fichaAvaliacao'),
    path('<int:id_ficha>/', views.ver_fichaAvaliacao, name='verFichaAvaliacao'),
    path('salvar/', views.salvar_ficha, name='salvarFichaAvaliacao'),
    path('agradecimento/', views.agradecimentos, name='agradecimentos'),
    path('entregues/', views.entregues, name='entregues'),
    path('qr_code/', views.gerar_qrcode, name='qr_code'),
    path('nao_respondeu/', views.salvar_nao_avaliacao, name='nao_avaliou'),
]
