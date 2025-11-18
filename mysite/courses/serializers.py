from .models import Course
from rest_framework import serializers
from assignments.serializers import CourseAssignmentSerializer


class CourseSerializer(serializers.ModelSerializer):
    assignments = CourseAssignmentSerializer(many=True, read_only=True)

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
            "course_assignments",
        ]
        read_only_fields = [
            "id",
            "teacher",
            "students",
            "course_assignments",
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
