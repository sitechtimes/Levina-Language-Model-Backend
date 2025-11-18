from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CourseSerializer
from assignments.serializers import AssignmentSerializer, CourseAssignmentSerializer
from users.serializers import UserSerializer
from .models import Course
from assignments.models import CourseAssignment
from utils.random import random_alphanumeric
from core.permissions import (
    IsStudent,
    IsTeacher,
    IsTeacherAndOwnsObject,
    IsAdmin,
    IsStudentAndOwnsObject,
    IsStudentAndIsInCourse,
)
from utils.permissions import UNSAFE_ACTIONS


class CourseViewSet(
    viewsets.ModelViewSet,
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS, "new_join_code", "join_code"]:
            permission_classes = [IsTeacherAndOwnsObject | IsAdmin]
        elif self.action in [
            "assignments",
            "students",
            "assignments",
            "assignment",
        ]:
            permission_classes = [
                IsStudentAndIsInCourse | IsTeacherAndOwnsObject | IsAdmin
            ]
        elif self.action == "join":
            permission_classes = [IsStudent]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        course = self.get_object()
        if request.user in course.students.all():
            return Response(
                "User already in course", status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("join_code") != course.join_code:
            return Response("Invalid join code", status=status.HTTP_400_BAD_REQUEST)
        course.students.add(request.user)
        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def new_join_code(self, request, pk=None):
        course = self.get_object()
        join_code = random_alphanumeric(6)
        course.join_code = join_code
        course.save()
        return Response(join_code)

    @action(detail=True, methods=["get"])
    def join_code(self, request, pk=None):
        course = self.get_object()
        return Response(course.join_code)

    @action(detail=True, methods=["get"])
    def assignments(self, request, pk=None):
        course = self.get_object()
        assignments = course.course_assignments.all()
        return Response(AssignmentSerializer(assignments, many=True).data)

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        course = self.get_object()
        students = course.students.all()
        return Response(UserSerializer(students, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"assignment/(?P<assignment_id>\d+)")
    def assignment(self, request, pk=None, assignment_id=None):
        course = self.get_object()
        try:
            course_assignment = CourseAssignment.objects.select_related(
                "assignment"
            ).get(course=course, assignment_id=assignment_id)
        except CourseAssignment.DoesNotExist:
            return Response(
                {"detail": "Assignment not found for this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CourseAssignmentSerializer(course_assignment).data)
