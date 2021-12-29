from django.urls import path
from . import views

urlpatterns = [
    path('<int:ordemdeservico_id>', views.verOrdem, name='verOrdem')
]
