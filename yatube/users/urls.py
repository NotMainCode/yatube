"""users URL Configuration."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path(
        "signup/",
        views.SignUp.as_view(template_name="users/signup.html"),
        name="signup",
    ),
]
