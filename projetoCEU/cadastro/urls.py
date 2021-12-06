from django.urls import path
from . import views

urlpatterns = [
    path('publico/', views.publico, name='publico'),
    path('colegio/', views.colegio, name='colegio'),
    path('empresa/', views.empresa, name='empresa')
]