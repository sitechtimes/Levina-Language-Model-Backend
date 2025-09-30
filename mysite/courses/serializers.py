from .models import Course
from rest_framework import serializers
from assignments.serializers import AssignmentSerializer


class CourseSerializer(serializers.ModelSerializer):
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "teacher", "students", "assignments"]
        read_only_fields = ["id", "teacher", "students", "assignments"]

    def create(self, validated_data):
        return Course.objects.create(
            title=validated_data["title"],
            description=validated_data["description"],
            teacher=self.context.get("request").user,
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.teacher = validated_data.get("teacher", instance.teacher)
        instance.save()
        return instance
