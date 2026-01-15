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
        ("EQ", "Essay Question"),
        ("AQ", "Audio Question"),
    ]

    question_type = models.CharField(choices=QUESTION_TYPES)
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    question_content_type = models.CharField(choices=CONTENT_TYPES)
    text_question = models.TextField(null=True, blank=True)
    audio_question = models.FileField(upload_to="questions/", null=True, blank=True)

    answer_content_type = models.CharField(choices=CONTENT_TYPES)
    text_answer = models.TextField(null=True, blank=True)

    assignments = models.ManyToManyField(
        "assignments.Assignment", related_name="questions", blank=True
    )
    assignment_templates = models.ManyToManyField(
        "assignments.AssignmentTemplate", related_name="questions", blank=True
    )

    def clean(self):
        # Validate question content matches question_content_type
        if self.question_content_type == "TEXT":
            if not self.text_question:
                raise ValidationError(
                    "Text question is required when question content type is TEXT"
                )
            if self.audio_question:
                raise ValidationError(
                    "Audio question should not be provided when question content type is TEXT"
                )
        elif self.question_content_type == "AUDIO":
            if not self.audio_question:
                raise ValidationError(
                    "Audio question is required when question content type is AUDIO"
                )
            if self.text_question:
                raise ValidationError(
                    "Text question should not be provided when question content type is AUDIO"
                )

        if self.question_type == "MCQ":
            if self.answer_content_type == "TEXT":
                if not self.text_answer:
                    raise ValidationError(
                        "Text answer is required for Multiple Choice Questions with TEXT answer type"
                    )
            elif self.answer_content_type == "AUDIO":
                if self.text_answer:
                    raise ValidationError(
                        "Text answer should not be provided when answer content type is AUDIO"
                    )


class QuestionInstance(models.Model):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    assignment_instance = models.ForeignKey(
        "assignments.AssignmentInstance",
        on_delete=models.CASCADE,
        related_name="question_instances",
    )
    text_answer = models.TextField(null=True, blank=True)
    audio_answer = models.FileField(upload_to="student_answers/", null=True, blank=True)
    submitted = models.BooleanField(default=False)


class SessionQuestionInstance(models.Model):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    session_instance = models.ForeignKey(
        "assignments.SessionInstance",
        on_delete=models.CASCADE,
        related_name="session_question_instances",
    )
    text_answer = models.TextField(null=True, blank=True)
    audio_answer = models.FileField(upload_to="session_answers/", null=True, blank=True)
    submitted = models.BooleanField(default=False)
