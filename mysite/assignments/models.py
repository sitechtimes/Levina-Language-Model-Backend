from django.db import models
from django.utils import timezone

# Create your models here.


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    timed = models.BooleanField(default=False)
    time_limit = models.IntegerField()
    teacher = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    @property
    def is_active(self):
        return timezone.now() < self.due_date


class AssignmentInstance(models.Model):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="assignment_instances",
    )
    student = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, null=True, blank=True
    )
    submitted = models.BooleanField(default=False)
    time_used = models.IntegerField(default=0)


class Session(models.Model):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    host = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    access_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)


class SessionInstance(models.Model):
    session = models.ForeignKey(
        "assignments.Session",
        on_delete=models.CASCADE,
        related_name="session_instances",
    )
    student_name = models.CharField(max_length=100)
    joined_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=128, unique=True, null=True, blank=True)
    submitted = models.BooleanField(default=False)
