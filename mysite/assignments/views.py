from core.permissions import (
    IsAdmin,
    IsStudentAndOwnsObject,
    IsTeacher,
)
from courses.models import Course
from django.utils.dateparse import parse_datetime
from questions.models import Question, QuestionInstance, SessionDialogueStatement
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from utils.create import assign_assignment, join_session
from utils.permissions import UNSAFE_ACTIONS
from utils.random import random_alphanumeric

from assignments.models import (
    Assignment,
    AssignmentInstance,
    AssignmentTemplate,
    Session,
    SessionInstance,
)
from assignments.serializers import (
    AssignmentInstanceSerializer,
    AssignmentSerializer,
    AssignmentTemplateSerializer,
    SessionInstanceSerializer,
    SessionSerializer,
)
from questions.models import Dialogue, DialogueStatement, DialogueInstance


class AssignmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = AssignmentTemplate.objects.all()
    serializer_class = AssignmentTemplateSerializer

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS, "assign"]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        assignment_template = self.get_object()
        try:
            course = Course.objects.get(id=request.data.get("course"))
        except Course.DoesNotExist:
            return Response("Course does not exist", status=status.HTTP_400_BAD_REQUEST)
        if course.assignments.filter(assignment_template=assignment_template).exists():
            return Response(
                "Assignment template already assigned to course",
                status=status.HTTP_400_BAD_REQUEST,
            )
        due_date = parse_datetime(request.data.get("due_date"))
        assignment = assign_assignment(assignment_template, course, due_date=due_date)
        return Response(
            AssignmentSerializer(assignment).data, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment_template = serializer.save(teacher=request.user)

        questions = request.data.get("questions")
        if questions:
            qs = Question.objects.filter(id__in=questions)
            assignment_template.questions.set(qs)
        dialogues = request.data.get("dialogues")
        if dialogues:
            ds = Dialogue.objects.filter(id__in=dialogues)
            assignment_template.dialogues.set(ds)

        return Response(
            AssignmentTemplateSerializer(assignment_template).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if new_questions := request.data.get("questions"):
            current_ids = set(instance.questions.values_list("id", flat=True))
            new_ids = set(new_questions)
            to_add = new_ids - current_ids
            to_remove = current_ids - new_ids
            if to_add:
                instance.questions.add(*to_add)
            if to_remove:
                instance.questions.remove(*to_remove)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            AssignmentTemplateSerializer(instance).data, status=status.HTTP_200_OK
        )


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save(teacher=request.user)
        questions = Question.objects.filter(id__in=request.data.get("questions", []))
        assignment.questions.set(questions)
        dialogues = Dialogue.objects.filter(id__in=request.data.get("dialogues", []))
        assignment.dialogues.set(dialogues)
        assignment_instances = [
            AssignmentInstance(
                assignment=assignment,
                student=student,
            )
            for student in assignment.course.students.all()
        ]
        AssignmentInstance.objects.bulk_create(assignment_instances)
        question_instances = [
            QuestionInstance(assignment_instance=assignment_instance, question=question)
            for question in assignment.questions.all()
            for assignment_instance in assignment_instances
        ]
        QuestionInstance.objects.bulk_create(question_instances)
        dialogue_instances = [
            DialogueInstance(
                dialogue=dialogue,
                assignment_instance=assignment_instance,
            )
            for dialogue in assignment.dialogues.all()
            for assignment_instance in assignment_instances
        ]
        DialogueInstance.objects.bulk_create(dialogue_instances)
        initial_statements = [
            DialogueStatement(
                dialogue_instance=dialogue_instance,
                audio=dialogue_instance.dialogue.initial_statement,
                author="AI",
            )
            for dialogue_instance in dialogue_instances
        ]
        DialogueStatement.objects.bulk_create(initial_statements)
        return Response(
            AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()
        if new_questions := request.data.get("questions"):
            current_ids = set(assignment.questions.values_list("id", flat=True))
            new_ids = set(new_questions)
            to_add = new_ids - current_ids
            to_remove = current_ids - new_ids
            if to_add:
                assignment.questions.add(*to_add)
                assignment_instances = assignment.assignment_instances.all()

                new_question_instances = [
                    QuestionInstance(
                        assignment_instance=assignment_instance,
                        question_id=question_id,
                    )
                    for assignment_instance in assignment_instances
                    for question_id in to_add
                ]

                QuestionInstance.objects.bulk_create(new_question_instances)
            if to_remove:
                assignment.questions.remove(*to_remove)
                QuestionInstance.objects.filter(
                    assignment_instance__assignment=assignment,
                    question_id__in=to_remove,
                ).delete()

        serializer = self.get_serializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        return Response(
            AssignmentSerializer(assignment).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentInstanceViewSet(viewsets.ModelViewSet):
    queryset = AssignmentInstance.objects.all()
    serializer_class = AssignmentInstanceSerializer

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsAdmin]
        elif self.action in ["submit", "increment_time_used"]:
            permission_classes = [IsStudentAndOwnsObject | IsAdmin]
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

    @action(detail=False, methods=["post"])
    def host_session(self, request):
        try:
            assignment_template = AssignmentTemplate.objects.get(
                id=request.data.get("assignment_template")
            )
        except AssignmentTemplate.DoesNotExist:
            return Response(
                "Assignment template does not exist", status=status.HTTP_400_BAD_REQUEST
            )
        session = Session.objects.create(
            assignment_template=assignment_template,
            host=request.user,
            access_code=random_alphanumeric(6),
        )
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def join_session(self, request):
        if not request.data.get("student_name"):
            return Response(
                "student_name is required", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            session = Session.objects.get(access_code=request.data.get("access_code"))
        except Session.DoesNotExist:
            return Response(
                "Session does not exist", status=status.HTTP_400_BAD_REQUEST
            )
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
    def add_dialogue_statement(self, request):
        session_instance = SessionInstance.objects.get(token=request.data.get("token"))
        if not session_instance.session.active:
            return Response("session_inactive", status=status.HTTP_400_BAD_REQUEST)
        session_dialogue_instance = session_instance.session_dialogue_instances.get(
            id=request.data.get("session_dialogue_instance")
        )
        if (
            session_dialogue_instance.statements.filter(author="STUDENT").count()
            >= session_dialogue_instance.dialogue.max_statements
        ):
            return Response(
                {"error": "Maximum number of statements reached."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.data.get("text") or request.data.get("text").strip() == "":
            return Response(
                {"error": "Text is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        student_statement = SessionDialogueStatement.objects.create(
            session_dialogue_instance=session_dialogue_instance,
            text=request.data.get("text"),
            author="STUDENT",
        )
        # replace with actual AI response generation logic
        ai_statement = SessionDialogueStatement.objects.create(
            session_dialogue_instance=session_dialogue_instance,
            text=f"AI response to: {request.data.get('text')}",
            author="AI",
        )
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
