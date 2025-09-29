from .models import Assignment, AssignmentInstance
from courses.models import Course
from rest_framework import serializers
from rest_framework.decorators import action


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "title", "due_date", "course"]

    def create(self, validated_data):
        # print("Validated Data: ", validated_data)
        print(self.request.user)
        # try:
        #     course = Course.objects.get(id=validated_data["course"])
        # except Course.DoesNotExist:
        #     raise serializers.ValidationError("Course does not exist")
        # print("Course:", course["id"])
        # return Assignment.objects.create(
        #     title=validated_data["title"],
        #     due_date=validated_data["due_date"],
        #     course=course,
        # )

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.due_date = validated_data.get("due_date", instance.due_date)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()


class AssignmentInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentInstance
        fields = ["id", "assignment", "student", "submitted", "answer"]
        read_only_fields = ["id", "assignment", "student"]

    def update(self, instance, validated_data):
        instance.submitted = validated_data.get("submitted", instance.submitted)
        instance.answer = validated_data.get("answer", instance.answer)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()

    @action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        instance = self.get_object()
        instance.answer = request.data["answer"]
        instance.save()
        return instance
