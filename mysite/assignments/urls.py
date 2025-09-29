from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AssignmentViewSet, AssignmentInstanceViewSet

router = DefaultRouter()
router.register("assignments", AssignmentViewSet)
router.register("assignment-instances", AssignmentInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
