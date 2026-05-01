from core.permissions import (
    IsAdmin,
    IsStudentAndOwnsAssignmentInstance,
    IsTeacher,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.permissions import UNSAFE_ACTIONS

from .models import (
    Dialogue,
    DialogueInstance,
    DialogueStatement,
    Question,
    QuestionInstance,
)
from .serializers import (
    DialogueInstanceSerializer,
    DialogueSerializer,
    DialogueStatementSerializer,
    QuestionInstanceSerializer,
    QuestionSerializer,
)


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assignments.exists():
            return Response(
                "Cannot delete question assigned to assignment.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionInstanceViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS, "submit"]:
            permission_classes = [IsStudentAndOwnsAssignmentInstance | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    serializer_class = QuestionInstanceSerializer
    queryset = QuestionInstance.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.assignment_instance.submitted:
            return Response(
                "Cannot update question instance that has been submitted.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(QuestionInstanceSerializer(instance).data, status=status.HTTP_200_OK)


class DialogueViewSet(viewsets.ModelViewSet):
    serializer_class = DialogueSerializer
    queryset = Dialogue.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    def create(self, request, *args, **kwargs):
        initial_statement_file = request.data.get("initial_statement")
        description = request.data.get("description")
        max_statements = request.data.get("max_statements")
        if not initial_statement_file:
            return Response(
                {"error": "Initial statement file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if initial_statement_file.content_type != "audio/mp4":
            return Response(
                {"error": "Initial statement file must be a WAV audio file."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not description or description.strip() == "" or type(description) != str:
            return Response(
                {"error": "Description is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if type(max_statements) == str and max_statements.isdigit():
            max_statements = int(max_statements)
        if not max_statements or type(max_statements) != int or max_statements <= 0:
            return Response(
                {"error": "Max length is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        dialogue = Dialogue.objects.create(
            description=request.data.get("description"),
            initial_statement=request.data.get("initial_statement"),
            max_statements=request.data.get("max_statements"),
        )
        return Response(DialogueSerializer(dialogue).data, status=status.HTTP_201_CREATED)


class DialogueStatementViewSet(viewsets.ModelViewSet):
    serializer_class = DialogueStatementSerializer
    queryset = DialogueStatement.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsTeacher | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]


class DialogueInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = DialogueInstanceSerializer
    queryset = DialogueInstance.objects.all()

    def get_permissions(self):
        if self.action in [*UNSAFE_ACTIONS]:
            permission_classes = [IsStudentAndOwnsAssignmentInstance | IsAdmin]
        else:
            permission_classes = []
        return [p() for p in permission_classes]

    @action(detail=True, methods=["post"])
    def add_statement(self, request, pk=None):
        dialogue_instance = self.get_object()
        if dialogue_instance.assignment_instance.submitted:
            return Response(
                "Cannot update question instance that has been submitted.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if dialogue_instance.statements.filter(author="STUDENT").count() >= dialogue_instance.dialogue.max_statements:
            return Response(
                {"error": "Maximum number of statements reached."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        audio_file = request.data.get("audio")
        if not audio_file:
            return Response(
                {"error": "Audio file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if audio_file.content_type != "audio/mp4":
            return Response(
                {"error": "Audio file must be a mp4 audio file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_statement = DialogueStatement.objects.create(
            dialogue_instance=dialogue_instance,
            audio=audio_file,
            author="STUDENT",
        )
        # replace with actual AI response generation logic
        DialogueStatement.objects.create(
            dialogue_instance=dialogue_instance,
            audio=audio_file,
            author="AI",
        )
        return Response(
            DialogueStatementSerializer(student_statement).data,
            status=status.HTTP_201_CREATED,
        )
