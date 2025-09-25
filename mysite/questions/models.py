from django.db import models
from users.models import CustomUser

# Create your models here.


class Question(models.Model):
    QUESTION_TYPES = [
        ("MCQ", "Multiple Choice Question"),
        ("EQ", "Essay Question"),
        ("AQ", "Audio Question"),
    ]
    question_type = models.CharField(choices=QUESTION_TYPES)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer = models.CharField()


class QuestionInstance(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer = models.CharField()
    submitted = models.BooleanField(default=False)
