from django.urls import path
from . import views

urlpatterns = [
    path('', views.detector_de_bombas, name='detector'),
    path('<int:id_detector>', views.detector_de_bombas, name='detector'),
]
