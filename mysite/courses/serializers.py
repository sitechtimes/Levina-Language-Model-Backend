from .models import Course
from rest_framework import serializers
from assignments.serializers import AssignmentSerializer
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    assignments = AssignmentSerializer(many=True, read_only=True)
    teachers = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "period",
            "class_type",
            "join_code",
            "teachers",
            "students",
            "assignments",
        ]
        read_only_fields = [
            "id",
            "teachers",
            "students",
            "assignments",
            "join_code",
        ]

    def create(self, validated_data):
        course= Course.objects.create(
            name=validated_data["name"],
            period=validated_data["period"],
            class_type=validated_data["class_type"],
        )
        course.teachers.add(self.context.get("request").user)
        return course

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.period = validated_data.get("period", instance.period)
        instance.class_type = validated_data.get("class_type", instance.class_type)
        instance.save()
        return instance
