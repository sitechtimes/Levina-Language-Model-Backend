from rest_framework import serializers

from .models import Question, QuestionInstance


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "answer",
            "author",
            "name",
            "audio_prompt",
        ]
        read_only_fields = ["id", "author"]


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
        read_only_fields = ["id", "submitted", "question"]


class ExpandedQuestionInstanceSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuestionInstance
        fields = [
            "id",
            "text_answer",
            "audio_answer",
            "submitted",
            "question",
        ]
        read_only_fields = ["id", "submitted"]
