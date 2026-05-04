from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DialogueInstanceViewSet,
    DialogueStatementViewSet,
    DialogueViewSet,
    QuestionInstanceViewSet,
    QuestionViewSet,
)

router = DefaultRouter()
router.register("questions", QuestionViewSet)
router.register("question-instances", QuestionInstanceViewSet)
router.register("dialogues", DialogueViewSet)
router.register("dialogue-statements", DialogueStatementViewSet)
router.register("dialogue-instances", DialogueInstanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
