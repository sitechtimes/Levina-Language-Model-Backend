from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import QuestionSerializer, QuestionInstanceSerializer
from .models import Question, QuestionInstance
from users.permissions import TeacherPermission, AdminPermission, SuperuserPermission, StudentPermission


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = [TeacherPermission | AdminPermission | SuperuserPermission]

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
