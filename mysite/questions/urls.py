from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuestionInstanceViewSet, QuestionViewSet

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("question-instances", QuestionInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
