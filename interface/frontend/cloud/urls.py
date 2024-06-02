from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("recharge/", views.recharge, name="recharge"),
    path("logout/", views.logout, name="logout"),
    path("create_container/", views.create_container, name="create_container"),
    path("delete_container/", views.delete_container_view, name="delete_container"),
    path("stop_container/", views.stop_container_view, name="stop_container"),
    path("pause_container/", views.pause_container_view, name="pause_container"),
    path("unpause_container/", views.unpause_container_view, name="unpause_container"),
    path("start_container/", views.start_container_view, name="start_container"),
    path("edit_container/", views.edit_container_view, name="edit_container"),
    path("profile/", views.profile, name="profile"),
]
