from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import QuestionViewSet, QuestionInstanceViewSet

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("question-instances", QuestionInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
