from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import QuestionSerializer, QuestionInstanceSerializer
from .models import Question, QuestionInstance


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class QuestionInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionInstanceSerializer
    queryset = QuestionInstance.objects.all()
