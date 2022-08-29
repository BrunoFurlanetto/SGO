from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ceu', views.dashboardCeu, name='dashboardCeu'),
    path('peraltas', views.dashboardPeraltas, name='dashboardPeraltas')
]
