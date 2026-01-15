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
            "false_answers",
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
        # Require question_type
        if not data.get("question_type"):
            raise serializers.ValidationError(
                {"question_type": "Question type is required"}
            )
        # Validate question_type
        if data.get("question_type") not in ["MCQ", "FRQ"]:
            raise serializers.ValidationError(
                {"question_type": "Invalid question type. Must be one of: MCQ, FRQ"}
            )

        # Validate question content matches question_content_type
        if data.get("question_content_type") == "TEXT":
            if not data.get("text_question"):
                raise serializers.ValidationError(
                    {
                        "text_question": "Text question is required when question content type is TEXT"
                    }
                )
            if data.get("audio_question"):
                raise serializers.ValidationError(
                    {
                        "audio_question": "Audio question should not be provided when question content type is TEXT"
                    }
                )
        elif data.get("question_content_type") == "AUDIO":
            if not data.get("audio_question"):
                raise serializers.ValidationError(
                    {
                        "audio_question": "Audio question is required when question content type is AUDIO"
                    }
                )
            if data.get("text_question"):
                raise serializers.ValidationError(
                    {
                        "text_question": "Text question should not be provided when question content type is AUDIO"
                    }
                )

        # Validate answer content for MCQ questions
        print(
            data.get("question_type"),
            data.get("answer_content_type"),
            data.get("text_answer"),
        )
        if data.get("question_type") == "MCQ":
            if data.get("answer_content_type") == "TEXT":
                if not data.get("text_answer"):
                    raise serializers.ValidationError(
                        {
                            "text_answer": "Text answer is required for Multiple Choice Questions with TEXT answer type"
                        }
                    )
            if data.get("answer_content_type") == "AUDIO":
                raise serializers.ValidationError(
                    {
                        "answer_content_type": "Audio answer type is not supported for Multiple Choice Questions"
                    }
                )
            if not data.get("false_answers"):
                raise serializers.ValidationError(
                    {
                        "false_answers": "False answers are required for Multiple Choice Questions"
                    }
                )
        if data.get("question_type") == "FRQ":
            if data.get("text_answer") or data.get("audio_answer"):
                raise serializers.ValidationError(
                    {
                        "answer": "Text and audio answers should not be provided when question type is FRQ."
                    }
                )
            if data.get("false_answers"):
                raise serializers.ValidationError(
                    {
                        "false_answers": "False answers are only allowed for Multiple Choice Questions"
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

    def validate(self, data):
        # Get the question instance to check answer_content_type
        question = self.instance.question if self.instance else None

        if question:
            # Validate answer content matches the question's answer_content_type
            if question.answer_content_type == "TEXT":
                if data.get("audio_answer"):
                    raise serializers.ValidationError(
                        {
                            "audio_answer": "Audio answer should not be provided when answer content type is TEXT"
                        }
                    )
            elif question.answer_content_type == "AUDIO":
                if data.get("text_answer"):
                    raise serializers.ValidationError(
                        {
                            "text_answer": "Text answer should not be provided when answer content type is AUDIO"
                        }
                    )

        return data
