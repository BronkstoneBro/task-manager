from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        views.CustomLogoutView.as_view(),
        name="logout",
    ),
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
]
