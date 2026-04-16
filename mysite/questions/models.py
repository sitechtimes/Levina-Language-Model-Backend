from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.


class Question(models.Model):
    CONTENT_TYPES = [
        ("TEXT", "Text"),
        ("AUDIO", "Audio"),
    ]

    QUESTION_TYPES = [
        ("MCQ", "Multiple Choice Question"),
        ("FRQ", "Free Response Question"),
    ]

    description = models.TextField(null=True, blank=True)

    question_type = models.CharField(choices=QUESTION_TYPES)
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    question_content_type = models.CharField(choices=CONTENT_TYPES)
    text_question = models.TextField(null=True, blank=True)
    audio_question = models.FileField(
        upload_to="audio/audio_questions/", null=True, blank=True
    )

    answer_content_type = models.CharField(choices=CONTENT_TYPES)
    text_answer = models.TextField(null=True, blank=True)
    false_answers = models.JSONField(null=True, blank=True)

    assignments = models.ManyToManyField(
        "assignments.Assignment", related_name="questions", blank=True
    )
    assignment_templates = models.ManyToManyField(
        "assignments.AssignmentTemplate", related_name="questions", blank=True
    )


class QuestionInstance(models.Model):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    assignment_instance = models.ForeignKey(
        "assignments.AssignmentInstance",
        on_delete=models.CASCADE,
        related_name="question_instances",
    )
    text_answer = models.TextField(null=True, blank=True)
    audio_answer = models.FileField(
        upload_to="audio/audio_answers/", null=True, blank=True
    )
    submitted = models.BooleanField(default=False)


class SessionQuestionInstance(models.Model):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    session_instance = models.ForeignKey(
        "assignments.SessionInstance",
        on_delete=models.CASCADE,
        related_name="session_question_instances",
    )
    text_answer = models.TextField(null=True, blank=True)
    audio_answer = models.FileField(
        upload_to="audio/session_audio_answers/", null=True, blank=True
    )
    submitted = models.BooleanField(default=False)


class DialogueQuestion(models.Model):
    STARTS_WITH_CHOICES = [
        ("AI", "AI"),
        ("STUDENT", "Student"),
    ]
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    prompt = models.TextField()
    starts_with = models.CharField(choices=STARTS_WITH_CHOICES, max_length=20)
    starting_statement = models.TextField(null=True, blank=True)


class DialogueQuestionInstance(models.Model):
    question = models.ForeignKey("questions.DialogueQuestion", on_delete=models.CASCADE)
    assignment_instance = models.ForeignKey(
        "assignments.AssignmentInstance",
        on_delete=models.CASCADE,
        related_name="dialogue_question_instances",
    )
    ai_statements = models.JSONField(null=True, blank=True)
    student_statements = models.JSONField(null=True, blank=True)
    submitted = models.BooleanField(default=False)
