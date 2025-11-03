from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CourseSerializer
from assignments.serializers import AssignmentSerializer
from users.serializers import UserSerializer
from .models import Course
from utils.random import random_alphanumberic


class CourseViewSet(
    viewsets.ModelViewSet,
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        course = self.get_object()
        course.students.add(request.user)
        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def join_code(self, request, pk=None):
        course = self.get_object()
        join_code = random_alphanumberic(6)
        course.join_code = join_code
        return Response(join_code)

    @action(detail=True, methods=["get"])
    def assignments(self, request, pk=None):
        course = self.get_object()
        assignments = course.assignments.all()
        return Response(AssignmentSerializer(assignments, many=True).data)

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        course = self.get_object()
        students = course.students.all()
        return Response(UserSerializer(students, many=True).data)
