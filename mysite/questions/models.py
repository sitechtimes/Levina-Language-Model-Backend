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
    answer = models.CharField()


class QuestionInstance(models.Model):
    title = models.CharField(max_length=100)
    question = models.ForeignKey("questions.Question", on_delete=models.CASCADE)
    student = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    answer = models.CharField()
    submitted = models.BooleanField(default=False)
