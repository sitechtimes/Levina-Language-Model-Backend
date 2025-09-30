from .models import Course
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "teacher", "students"]
        read_only_fields = ["id", "teacher", "students"]

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
