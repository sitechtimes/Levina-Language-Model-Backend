from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CourseSerializer
from .models import Course


class CourseViewSet(
    viewsets.ModelViewSet,
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        course = self.get_object()
        request.user.courses.add(course)
        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )
