from django.urls import path
from . import views

urlpatterns = [
    path('', views.escala, name='escala'),
    path('disponibilidade/', views.disponibilidade, name='disponibilidade'),
    path('disponibilidade/ceu/visualizar/', views.visualizarDisponibilidadeCeu, name='visualizarDisponibilidadeCeu'),
    path('disponibilidade_peraltas/', views.disponibilidadePeraltas, name='disponibilidadePeraltas'),
    path('disponibilidade_peraltas/visualizar/', views.visualizarDisponibilidadePeraltas,
         name='visualizarDisponibilidadePeraltas'),
    path('disponibilidade_peraltas/verificar_dias_hospedagem/', views.verificar_hospedagem,
         name='verificar_dias_hospedagem'),
    path('disponibilidade_peraltas/alterar_dias_disponibilidade/', views.alterar_dias_disponibilidade,
         name='alterar_dias_disponibilidade'),
    path('peraltas/', views.verEscalaPeraltas, name='escalaPeraltas'),
    path('peraltas/acampamento/', views.ver_escalas_acampamento, name='ver_escalas_acampamento'),
    path('peraltas/hotelaria/', views.ver_escalas_hotelaria, name='ver_escalas_hotelaria'),
    path('peraltas/escalas_monitor/', views.ver_escalas_monitor, name='ver_escalas_monitor'),
    path('peraltas/montar_escala/', views.montar_escala, name='montar_escala'),
    path('peraltas/confirmar_escala/', views.confirmar_escala, name='confirmar_escala'),
    path('peraltas/deletar_escala/', views.deletar_escala, name='deletar_escala'),
    path('peraltas/gerar_pdf_escala/', views.gerar_pdf_escala, name='gerar_pdf_escala'),
    path('peraltas/verificar_setor/', views.verificar_hospedagem, name='verificar_setor'),
    path('peraltas/<str:setor>/escalar/<str:data>/', views.escalarMonitores, name='escalar_monitores'),
    path('peraltas/<str:setor>/escalar/<str:data>/<int:id_cliente>/', views.escalarMonitores,
         name='editar_escala_monitores'),
]
