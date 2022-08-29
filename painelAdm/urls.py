from django.urls import path
from . import views

urlpatterns = [
    path('', views.painelGeral, name='painelGeral')
]
