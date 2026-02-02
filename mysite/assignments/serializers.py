from questions.serializers import (
    QuestionInstanceSerializer,
    QuestionSerializer,
)
from rest_framework import serializers

from .models import (
    Assignment,
    AssignmentInstance,
    AssignmentTemplate,
    Session,
    SessionInstance,
)


class AssignmentInstanceSerializer(serializers.ModelSerializer):
    question_instances = QuestionInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = AssignmentInstance
        fields = [
            "id",
            "assignment",
            "student",
            "submitted",
            "time_used",
            "question_instances",
        ]
        read_only_fields = [
            "id",
            "assignment",
            "student",
            "question_instances",
        ]

    def delete(self, instance):
        instance.delete()


class AssignmentTemplateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = AssignmentTemplate
        fields = [
            "id",
            "name",
            "timed",
            "time_limit",
            "teacher",
            "questions",
        ]

        read_only_fields = [
            "id",
            "teacher",
            "questions",
        ]

    def create(self, validated_data):
        teacher = self.context.get("request").user
        return AssignmentTemplate.objects.create(
            name=validated_data["name"],
            teacher=teacher,
            timed=validated_data["timed"],
            time_limit=validated_data["time_limit"],
        )


class AssignmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    assignment_instances = AssignmentInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "name",
            "due_date",
            "is_active",
            "timed",
            "time_limit",
            "teacher",
            "course",
            "date_assigned",
            "assignment_instances",
            "questions",
        ]

        read_only_fields = [
            "id",
            "teacher",
            "assignment_instances",
            "questions",
            "date_assigned",
            "is_active",
        ]

    def create(self, validated_data):
        teacher = self.context.get("request").user
        return Assignment.objects.create(
            name=validated_data["name"],
            due_date=validated_data["due_date"],
            teacher=teacher,
            timed=validated_data["timed"],
            time_limit=validated_data["time_limit"],
            course=validated_data["course"],
        )

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        instance.timed = validated_data.get("timed", instance.timed)
        instance.time_limit = validated_data.get("time_limit", instance.time_limit)
        instance.save()
        return instance


class SessionInstanceSerializer(serializers.ModelSerializer):
    session_question_instances = QuestionInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = SessionInstance
        fields = [
            "id",
            "session",
            "student_name",
            "joined_at",
            "submitted",
            "session_question_instances",
        ]
        read_only_fields = [
            "id",
            "session",
            "joined_at",
            "submitted",
            "session_question_instances",
        ]


class SessionSerializer(serializers.ModelSerializer):
    session_instances = SessionInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "assignment_template",
            "host",
            "access_code",
            "active",
            "session_instances",
        ]
        read_only_fields = [
            "id",
            "assignment_template",
            "host",
            "active",
            "session_instances",
        ]

    def destroy(self, instance):
        if instance.session_instances.exists():
            raise serializers.ValidationError(
                "Cannot delete session with active session instances."
            )
