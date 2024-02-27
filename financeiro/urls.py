from django.urls import path

from . import views

urlpatterns = [
    path('', views.ficha_financeira, name='financeira'),
]
