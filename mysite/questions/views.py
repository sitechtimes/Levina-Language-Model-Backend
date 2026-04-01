from core.permissions import (
    IsAdmin,
    IsStudentAndOwnsAssignmentInstance,
    IsTeacher,
)
from rest_framework import status, viewsets
from rest_framework.response import Response
from utils.permissions import UNSAFE_ACTIONS

from .models import Question, QuestionInstance, DialogueQuestion
from .serializers import (
    QuestionInstanceSerializer,
    QuestionSerializer,
    DialogueQuestionSerializer,
)


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        if self.action in [*UNSAFE_ACTIONS, "submit"]:
            permission_classes = [IsStudentAndOwnsAssignmentInstance | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    serializer_class = QuestionInstanceSerializer
    queryset = QuestionInstance.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assignment_instance.submitted:
            return Response(
                "Cannot update question instance that has been submitted.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            QuestionInstanceSerializer(instance).data, status=status.HTTP_200_OK
        )


class DialogueQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = DialogueQuestionSerializer
    queryset = DialogueQuestion.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
