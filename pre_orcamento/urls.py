from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard_pre_orcamento'),
    path('novo/', views.nova_previa, name='nova_previa'),
    path('validar_pacotes/', views.validar_pacotes, name='validar_pacotes'),
]
