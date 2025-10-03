from .models import Question, QuestionInstance
from rest_framework import serializers


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "answer",
            "author",
            "title",
        ]


class QuestionInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionInstance
        fields = [
            "id",
            "text_answer",
            "audio_answer",
            "submitted",
            "question",
        ]
