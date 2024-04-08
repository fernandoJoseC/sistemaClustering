from django.urls import path, include
from .views import authView, home, inicioView, introduccionView
urlpatterns = [
    path("", home, name="home"),
    path("signup/", authView, name="authView"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("inicio/", inicioView, name="inicioView"),
    path("introduccion/", introduccionView, name="introduccionView"),


]
