from django.urls import path
from . import views

urlpatterns = [
    path('', views.ordem, name='orden_servico')
]
