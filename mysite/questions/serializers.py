from .models import Question, QuestionInstance
from rest_framework import serializers


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_type", "answer", "author"]


class QuestionInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionInstance
        fields = ["id", "answer", "submitted", "question", "student"]
