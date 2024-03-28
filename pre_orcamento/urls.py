from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard_pre_orcamento'),
    path('novo/', views.nova_previa, name='nova_previa'),
]
