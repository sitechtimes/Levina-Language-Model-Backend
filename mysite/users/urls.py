from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PasswordResetConfirmView, PasswordResetRequestView, GetUserView

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
