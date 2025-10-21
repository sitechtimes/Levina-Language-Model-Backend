from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.permissions import IsStudent, IsTeacher, IsAdmin, IsOwner
from .serializers import QuestionSerializer, QuestionInstanceSerializer
from .models import Question, QuestionInstance


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def get_permissions(self):
        if self.action == "join":
            perms = [IsStudent]
        elif self.action in [
            "list",
            "retrieve",
            "join_code",
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            perms = [IsTeacher | IsAdmin]
        return [p() for p in perms]

    def create(self, request, *args, **kwargs):
        question = Question.objects.create(
            title=request.data["title"],
            question_type=request.data["question_type"],
            author=self.request.user,
        )
        return Response(
            QuestionSerializer(question).data, status=status.HTTP_201_CREATED
        )


class QuestionInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionInstanceSerializer
    queryset = QuestionInstance.objects.all()

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            perms = [IsStudent & IsOwner]
        elif self.action == "list":
            perms = [IsTeacher | IsAdmin]
        else:
            perms = [IsAdmin]
        return [p() for p in perms]
