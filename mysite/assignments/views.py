from rest_framework import mixins, viewsets, status
from .serializers import CourseSerializer
from .models import Assignment, AssignmentInstance


class CourseViewSet(
    viewsets.ModelViewSet,
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
