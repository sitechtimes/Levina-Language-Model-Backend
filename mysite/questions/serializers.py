from rest_framework import serializers

from .models import Question, QuestionInstance


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "author",
            "question_content_type",
            "text_question",
            "audio_question",
            "answer_content_type",
            "text_answer",
        ]
        read_only_fields = ["id", "author"]

    def validate(self, data):
        # Require question_content_type and answer_content_type
        if not data.get("question_content_type"):
            raise serializers.ValidationError(
                {"question_content_type": "Question content type is required"}
            )
        if not data.get("answer_content_type"):
            raise serializers.ValidationError(
                {"answer_content_type": "Answer content type is required"}
            )

        # Validate question content
        if data.get("question_content_type") == "TEXT" and not data.get(
            "text_question"
        ):
            raise serializers.ValidationError(
                {
                    "text_question": "Text question is required when question content type is TEXT"
                }
            )
        if data.get("question_content_type") == "AUDIO" and not data.get(
            "audio_question"
        ):
            raise serializers.ValidationError(
                {
                    "audio_question": "Audio question is required when question content type is AUDIO"
                }
            )

        if data.get("question_type") == "MCQ":
            if data.get("answer_content_type") == "TEXT" and not data.get(
                "text_answer"
            ):
                raise serializers.ValidationError(
                    {
                        "text_answer": "Text answer is required for Multiple Choice Questions"
                    }
                )
            if len(data.get("text_answer")) == 0:
                raise serializers.ValidationError(
                    {
                        "text_answer": "Text answer is required for Multiple Choice Questions"
                    }
                )
            if data.get("answer_content_type") == "AUDIO":
                raise serializers.ValidationError(
                    {
                        "audio_answer": "Audio answer is not supported for Multiple Choice Questions"
                    }
                )

        return data


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
