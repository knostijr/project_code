"""
URL configuration for accounts app - Authentication.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
]