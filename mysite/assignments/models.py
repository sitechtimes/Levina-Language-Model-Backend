from django.db import models
from users.models import CustomUser

# Create your models here.


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    timed = models.BooleanField(default=False)
    time_limit = models.DurationField()
    teacher = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    questions = models.ManyToManyField("questions.Question", related_name="assignments")


class AssignmentInstance(models.Model):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="assignment_instances",
    )
    student = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    answer = models.CharField()
    submitted = models.BooleanField(default=False)
