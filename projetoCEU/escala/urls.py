from django.urls import path
from . import views

urlpatterns = [
    path('', views.escala, name='escala'),
]
