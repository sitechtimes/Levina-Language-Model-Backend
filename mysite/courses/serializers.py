from .models import Course
from rest_framework import serializers
from assignments.serializers import AssignmentSerializer


class CourseSerializer(serializers.ModelSerializer):
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
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
            period=validated_data["period"],
            class_type=validated_data["class_type"],
            teacher=self.context.get("request").user,
        )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.period = validated_data.get("period", instance.period)
        instance.class_type = validated_data.get("class_type", instance.class_type)
        instance.save()
        return instance
