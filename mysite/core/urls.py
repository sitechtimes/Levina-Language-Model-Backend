from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include("users.urls")),
    path("", include("courses.urls")),
    path("", include("assignments.urls")),
    path("", include("questions.urls")),
    path("users/", include("users.urls")),
]
