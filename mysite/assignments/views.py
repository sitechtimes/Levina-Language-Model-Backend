from rest_framework import viewsets, status
from rest_framework.response import Response
from assignments.serializers import (
    AssignmentSerializer,
    CourseAssignmentSerializer,
    AssignmentInstanceSerializer,
    SessionSerializer,
    SessionInstanceSerializer,
)
from assignments.models import (
    Assignment,
    CourseAssignment,
    AssignmentInstance,
    Session,
    SessionInstance,
)
from questions.models import Question
from utils.random import random_alphanumeric
from core.permissions import (
    IsStudent,
    IsTeacher,
    IsTeacherAndOwnsObject,
    IsAdmin,
    IsStudentAndOwnsObject,
)
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from utils.create import assign_assignment, join_session
from utils.permissions import UNSAFE_ACTIONS


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in UNSAFE_ACTIONS:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        if "course" not in request.data:
            return Response(
                {"error": "Course is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save(teacher=request.user)

        questions = request.data.get("questions")
        if questions:
            qs = Question.objects.filter(id__in=questions)
            assignment.questions.set(qs)

        return Response(
            AssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


class CourseAssignmentViewSet(viewsets.ModelViewSet):
    queryset = CourseAssignment.objects.all()
    serializer_class = CourseAssignmentSerializer

    def get_permissions(self):
        if self.action in UNSAFE_ACTIONS:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assignment_instances.exists():
            return Response(
                "Cannot delete assignment that has been assigned to students.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsAdmin]
        elif self.action in ["submit", "increment_time_used"]:
            permission_classes = [IsStudentAndOwnsObject]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        instance = self.get_object()

        if instance.submitted:
            return Response(
                "Assignment_already_submitted",
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.submitted = True
        instance.save()

        # Mark all related question_instances as submitted
        instance.question_instances.all().update(submitted=True)

        return Response(
            AssignmentInstanceSerializer(instance).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def increment_time_used(self, request, pk=None):
        instance = self.get_object()

        # Must be int; request.data may be a string
        try:
            delta = int(request.data.get("time_used", 0))
        except ValueError:
            return Response(
                "Invalid time_used value",
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.time_used += delta
        instance.save()

        return Response(
            AssignmentInstanceSerializer(instance).data,
            status=status.HTTP_200_OK,
        )


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def get_permissions(self):
        if self.action in [
            *UNSAFE_ACTIONS,
            "host_session",
            "end_session",
        ]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    @action(detail=True, methods=["post"])
    def host_session(self, request, pk=None):
        assignment = Assignment.objects.get(id=pk)
        print(request.user)
        session = Session.objects.create(
            assignment=assignment,
            host=request.user,
            access_code=random_alphanumeric(6),
        )
        return Response(
            SessionSerializer(session).data, status=status.HTTP_201_CREATED
        ) @ action(detail=False, methods=["post"])

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
