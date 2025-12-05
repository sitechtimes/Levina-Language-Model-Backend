from django.urls import path

from .views import GetUserView, PasswordResetConfirmView, PasswordResetRequestView

urlpatterns = [
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("get-user/", GetUserView.as_view(), name="get-user"),
]
