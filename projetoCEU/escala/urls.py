from django.urls import path
from . import views

urlpatterns = [
    path('', views.escala, name='escala'),
    path('disponibilidade/', views.disponibilidade, name='disponibilidade'),
    path('montar_escala/', views.MontarEscalaCeu, name='montarEscala'),
    path('disponibilidade/ceu/visualizar/', views.visualizarDisponibilidadeCeu, name='visualizarDisponibilidadeCeu'),
    path('disponibilidade_peraltas/', views.disponibilidadePeraltas, name='disponibilidadePeraltas'),
    path('disponibilidade_peraltas/visualizar', views.visualizarDisponibilidadePeraltas,
         name='visualizarDisponibilidadePeraltas'),
    path('peraltas/', views.verEscalaPeraltas, name='escalaPeraltas'),
    path('peraltas/<str:setor>/escalar/<str:data>', views.escalarMonitores, name='escalar_monitores'),
    path('acampamento/editar/evento/<str:cliente>/<str:data>', views.editarEscalaMonitores, name='editar_escala'),
    path('hotelaria/editar/<str:data>', views.editarEscalaHotelaria, name='editar_escala_hotelaria'),
]
