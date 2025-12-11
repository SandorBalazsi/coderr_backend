from django.urls import path
from .api import views

urlpatterns = [
    path('registration/', views.RegisterView.as_view(), name='auth_register'),
    path('login/', views.LoginView.as_view(), name='auth_login'),
]