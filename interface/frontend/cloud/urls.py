from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("recharge/", views.recharge, name="recharge"),
    path("logout/", views.logout, name="logout")
]
