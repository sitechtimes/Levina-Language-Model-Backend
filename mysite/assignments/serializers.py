from .models import Assignment, AssignmentInstance
from courses.models import Course
from rest_framework import serializers
from questions.serializers import QuestionSerializer


class AssignmentInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentInstance
        fields = ["id", "assignment", "student", "submitted"]
        read_only_fields = ["id", "assignment", "student"]

    def update(self, instance, validated_data):
        instance.submitted = validated_data.get("submitted", instance.submitted)
        instance.answer = validated_data.get("answer", instance.answer)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()


class AssignmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    assignment_instances = AssignmentInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "due_date",
            "timed",
            "time_limit",
            "teacher",
            "assignment_instances",
            "questions",
        ]

        read_only_fields = [
            "id",
            "teacher",
            "assignment_instances",
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

    def delete(self, instance):
        instance.delete()
