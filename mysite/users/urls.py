from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PasswordResetConfirmView, PasswordResetRequestView

router = DefaultRouter()
router.register(
    "password-reset-request",
    PasswordResetRequestView,
)
router.register(
    "password-reset-confirm",
    PasswordResetConfirmView,
)

urlpatterns = [
    path("", include(router.urls)),
]
