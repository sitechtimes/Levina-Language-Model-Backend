from .models import Course
from rest_framework import serializers
from assignments.serializers import AssignmentSerializer
from assignments.models import CourseAssignment


class CourseSerializer(serializers.ModelSerializer):
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "period",
            "class_type",
            "join_code",
            "teacher",
            "students",
            "assignments",
        ]
        read_only_fields = [
            "id",
            "teacher",
            "students",
            "assignments",
            "join_code",
        ]

    def create(self, validated_data):
        return Course.objects.create(
            title=validated_data["title"],
            description=validated_data["description"],
            period=validated_data["period"],
            class_type=validated_data["class_type"],
            teacher=self.context.get("request").user,
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.period = validated_data.get("period", instance.period)
        instance.class_type = validated_data.get("class_type", instance.class_type)
        instance.save()
        return instance


class FlatCourseAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="assignment.id", read_only=True)
    title = serializers.CharField(source="assignment.title", read_only=True)
    due_date = serializers.DateTimeField(source="assignment.due_date", read_only=True)
    is_active = serializers.BooleanField(source="assignment.is_active", read_only=True)
    timed = serializers.BooleanField(source="assignment.timed", read_only=True)
    time_limit = serializers.IntegerField(
        source="assignment.time_limit", read_only=True
    )
    teacher = serializers.IntegerField(source="assignment.teacher.id", read_only=True)

    questions = AssignmentSerializer(source="assignment").fields["questions"]
    assignment_instances = AssignmentSerializer(source="assignment").fields[
        "assignment_instances"
    ]

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
            "questions",
            "assignment_instances",
            "date_assigned",
        ]
