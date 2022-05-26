from django.urls import path
from . import views

urlpatterns = [
    path('', views.escala, name='escala'),
    path('disponibilidade/', views.disponibilidade, name='disponibilidade'),
    path('disponibilidade_peraltas/', views.disponibilidadePeraltas, name='disponibilidadePeraltas'),
    path('peraltas/', views.verEscalaPeraltas, name='escalaPeraltas'),
    path('peraltas/<str:setor>/escalar/<str:data>', views.escalarMonitores, name='escalar_monitores'),
]
