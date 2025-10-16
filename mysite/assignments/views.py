from rest_framework import mixins, viewsets, status
from .serializers import (
    AssignmentSerializer,
    AssignmentInstanceSerializer,
    SessionSerializer,
    SessionInstanceSerializer,
)
from courses.models import Course
from .models import Assignment, AssignmentInstance, Session, SessionInstance
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.create import assign_assignment
from utils.random import random_alphanumberic


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
        assign_assignment(instance, course)
        return Response(
            AssignmentSerializer(instance).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def host_session(self, request, pk=None):
        instance = self.get_object()
        print(request.user)
        session = Session.objects.create(
            assignment=instance,
            host=request.user,
            access_code=random_alphanumberic(6),
        )
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)

    def join_session(self, request, pk=None):
        instance = self.get_object()
        AssignmentInstance.objects.create(
            assignment=instance, student_name=request.data["student_name"]
        )
        return Response(AssignmentInstanceSerializer(instance).data)


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.submitted:
            return Response(
                "Assignment already submitted", status=status.HTTP_400_BAD_REQUEST
            )
        instance.submitted = True
        instance.save()
        instance.question_instances.all().update(submitted=True)
        return Response(
            AssignmentInstanceSerializer(instance).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def increment_time_used(self, request, pk=None):
        instance = self.get_object()
        instance.time_used += int(request.data.get("time_used"))
        instance.save()
        return Response(AssignmentInstanceSerializer(instance).data)
