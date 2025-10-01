from django.db import models
from users.models import CustomUser

# Create your models here.


class Question(models.Model):
    QUESTION_TYPES = [
        ("MCQ", "Multiple Choice Question"),
        ("EQ", "Essay Question"),
        ("AQ", "Audio Question"),
    ]
    title = models.CharField(max_length=100)
    question_type = models.CharField(choices=QUESTION_TYPES)
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    answer = models.CharField(null=True, blank=True)


class QuestionInstance(models.Model):
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    assignment_instance = models.ForeignKey(
        "assignments.AssignmentInstance", on_delete=models.CASCADE
    )
    text_answer = models.CharField(null=True, blank=True)  # for MCQ or EQ
    audio_answer = models.FileField(null=True, blank=True)  # for AQ
    submitted = models.BooleanField(default=False)
