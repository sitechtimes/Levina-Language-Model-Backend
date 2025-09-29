from rest_framework import mixins, viewsets, status
from .serializers import AssignmentSerializer, AssignmentInstanceSerializer
from .models import Assignment, AssignmentInstance


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer
