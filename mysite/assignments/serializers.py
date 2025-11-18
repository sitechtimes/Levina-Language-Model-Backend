from .models import (
    Assignment,
    CourseAssignment,
    AssignmentInstance,
    Session,
    SessionInstance,
)

from rest_framework import serializers
from questions.serializers import (
    QuestionSerializer,
    QuestionInstanceSerializer,
    ExpandedQuestionInstanceSerializer,
)


class AssignmentInstanceSerializer(serializers.ModelSerializer):
    question_instances = QuestionInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = AssignmentInstance
        fields = [
            "id",
            "course_assignment",
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


class AssignmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "due_date",
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
        return Assignment.objects.create(
            title=validated_data["title"],
            due_date=validated_data["due_date"],
            teacher=teacher,
            timed=validated_data["timed"],
            time_limit=validated_data["time_limit"],
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        instance.save()
        return instance


class CourseAssignmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    assignment_instances = AssignmentInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = CourseAssignment
        fields = [
            "id",
            "title",
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
            title=validated_data["title"],
            due_date=validated_data["due_date"],
            teacher=teacher,
            timed=validated_data["timed"],
            time_limit=validated_data["time_limit"],
            course=validated_data["course"],
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        instance.save()
        return instance


class SessionInstanceSerializer(serializers.ModelSerializer):
    session_question_instances = ExpandedQuestionInstanceSerializer(
        many=True, read_only=True
    )

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
            "assignment",
            "host",
            "access_code",
            "active",
            "session_instances",
        ]
        read_only_fields = ["id", "assignment", "host", "active", "session_instances"]

    def destroy(self, instance):
        if instance.session_instances.exists():
            raise serializers.ValidationError(
                "Cannot delete session with active session instances."
            )
