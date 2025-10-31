from rest_framework import mixins, viewsets, status
from .serializers import (
    AssignmentSerializer,
    AssignmentInstanceSerializer,
    SessionSerializer,
    SessionInstanceSerializer,
)
from courses.models import Course
from questions.models import Question
from .models import Assignment, AssignmentInstance, Session, SessionInstance
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from utils.create import assign_assignment, join_session
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

    def create(self, request, *args, **kwargs):
        questions = request.data.get("questions")
        if not questions:
            return Response(
                "At least one question is required", status=status.HTTP_400_BAD_REQUEST
            )
        question_set = Question.objects.filter(id__in=questions)
        assignment = Assignment.objects.create(
            title=request.data["title"],
            due_date=request.data["due_date"],
            timed=request.data["timed"],
            time_limit=request.data["time_limit"],
            teacher=self.request.user,
        )
        assignment.questions.set(question_set)
        return Response(
            AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.courses.exists():
            return Response(
                "Cannot delete assignment assigned to courses.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=["post"])
    def host_session(self, request, pk=None):
        assignment = Assignment.objects.get(id=pk)
        print(request.user)
        session = Session.objects.create(
            assignment=assignment,
            host=request.user,
            access_code=random_alphanumberic(6),
        )
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def join_session(self, request):
        if not request.data.get("student_name"):
            return Response(
                "student_name is required", status=status.HTTP_400_BAD_REQUEST
            )
        session = Session.objects.get(access_code=request.data.get("access_code"))
        session_instance, token = join_session(
            session=session, student_name=request.data.get("student_name")
        )
        return Response(
            {
                "session_instance": SessionInstanceSerializer(session_instance).data,
                "token": session_instance.token,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def end_session(self, request, pk=None):
        session = self.get_object()
        if not session.active:
            return Response(
                "Session already inactive", status=status.HTTP_400_BAD_REQUEST
            )
        session.active = False
        session.save()
        return Response(SessionSerializer(session).data)


class SessionInstanceViewSet(viewsets.ModelViewSet):
    queryset = SessionInstance.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def update_answer(self, request):
        session_instance = SessionInstance.objects.get(token=request.data.get("token"))
        if not session_instance.session.active:
            return Response("session_inactive", status=status.HTTP_400_BAD_REQUEST)
        session_question_instance = session_instance.session_question_instances.get(
            id=request.data.get("question_instance")
        )
        if request.data.get("text_answer"):
            session_question_instance.text_answer = request.data.get("text_answer")
        elif request.data.get("audio_answer"):
            session_question_instance.audio_answer = request.data.get("audio_answer")
        else:
            return Response("answer_required", status=status.HTTP_400_BAD_REQUEST)
        session_question_instance.save()

        return Response(
            SessionInstanceSerializer(session_instance).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def submit(self, request, pk=None):
        session_instance = SessionInstance.objects.get(token=request.data.get("token"))
        if not session_instance.session.active:
            return Response("session_inactive", status=status.HTTP_400_BAD_REQUEST)
        if session_instance.submitted:
            return Response(
                "SessionInstance_already_submitted", status=status.HTTP_400_BAD_REQUEST
            )
        session_instance.submitted = True
        session_instance.save()
        return Response(
            SessionInstanceSerializer(session_instance).data,
            status=status.HTTP_200_OK,
        )


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer

    @action(detail=False, methods=["post"])
    def submit(self, request, pk=None):
        instance = self.get_object()
        if instance.submitted:
            return Response(
                "Assignment_already_submitted", status=status.HTTP_400_BAD_REQUEST
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
