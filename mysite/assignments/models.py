from django.db import models

# Create your models here.


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    timed = models.BooleanField(default=False)
    time_limit = models.IntegerField()
    teacher = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)


class AssignmentInstance(models.Model):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="assignment_instances",
    )
    student = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    time_used = models.IntegerField(default=0)
