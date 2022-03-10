from django.urls import path
from . import views

urlpatterns = [
    path('ceu', views.dashboardCeu, name='dashboardCeu'),
    path('peraltas', views.dashboardPeraltas, name='dashboardPeraltas')
]
