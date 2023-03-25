from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='login'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='nova_senha'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('trocar_senha/', auth_views.PasswordChangeView.as_view(), name='alterar_senha'),
    path('logout/', views.logout, name='logout'),
]
