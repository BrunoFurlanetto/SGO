from django.urls import path
from . import views

urlpatterns = [
    path('', views.eventos, name='calendario_eventos')
]
