from django.urls import path

from . import views


urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("register/", views.register, name="register"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post_delete"),
]
