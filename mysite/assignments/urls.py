from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    AssignmentViewSet,
    AssignmentInstanceViewSet,
    SessionViewSet,
    SessionInstanceViewSet,
)

router = DefaultRouter()
router.register("assignments", AssignmentViewSet)
router.register("assignment-instances", AssignmentInstanceViewSet)
router.register("sessions", SessionViewSet)
router.register("session-instances", SessionInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
