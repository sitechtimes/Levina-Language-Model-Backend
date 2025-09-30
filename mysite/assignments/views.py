from rest_framework import mixins, viewsets, status
from .serializers import AssignmentSerializer, AssignmentInstanceSerializer
from courses.models import Course
from .models import Assignment, AssignmentInstance
from rest_framework.decorators import action
from rest_framework.response import Response


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        instance = self.get_object()
        course = Course.objects.get(id=request.data["course"])
        if instance in course.assignments.all():
            return Response(
                "Assignment already assigned", status=status.HTTP_400_BAD_REQUEST
            )
        assignment_instances = [
            AssignmentInstance(
                assignment=instance,
                student=student,
            )
            for student in course.students.all()
        ]
        AssignmentInstance.objects.bulk_create(assignment_instances)
        return Response(
            AssignmentSerializer(instance).data, status=status.HTTP_201_CREATED
        )


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        instance = self.get_object()
        instance.submitted = True
        instance.save()
        return Response(
            AssignmentInstanceSerializer(instance).data, status=status.HTTP_201_CREATED
        )
