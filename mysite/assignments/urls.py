from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentInstanceViewSet,
    AssignmentTemplateViewSet,
    AssignmentViewSet,
    SessionInstanceViewSet,
    SessionViewSet,
)

router = DefaultRouter()
router.register("assignment-templates", AssignmentTemplateViewSet)
router.register("assignments", AssignmentViewSet)
router.register("assignment-instances", AssignmentInstanceViewSet)
router.register("sessions", SessionViewSet)
router.register("session-instances", SessionInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
