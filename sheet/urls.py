from django.urls import path

from .views import home, login, register

urlpatterns = [
    path("", home, name="home"),
    path("", home, name="logout"),
    path("login", login, name="login"),
    path("register", register, name="register"),
]
