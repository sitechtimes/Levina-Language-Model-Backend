from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuestionInstanceViewSet, QuestionViewSet, DialogueQuestionViewSet

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("question-instances", QuestionInstanceViewSet)
router.register("dialogue-questions", DialogueQuestionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
