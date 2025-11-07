from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import QuestionSerializer, QuestionInstanceSerializer
from .models import Question, QuestionInstance
from core.permissions import (
    IsStudent,
    IsTeacher,
    IsAdmin,
    IsStudentAndOwnsObject,
    IsStudentAndOwnsAssignmentInstance,
)
from utils.permissions import UNSAFE_ACTIONS


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        question = Question.objects.create(
            title=request.data["title"],
            question_type=request.data["question_type"],
            author=self.request.user,
        )
        return Response(
            QuestionSerializer(question).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assignments.exists():
            return Response(
                "Cannot delete question assigned to assignment.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionInstanceViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsStudentAndOwnsAssignmentInstance]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    serializer_class = QuestionInstanceSerializer
    queryset = QuestionInstance.objects.all()
