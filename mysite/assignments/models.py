from django.db import models
from users.models import CustomUser

# Create your models here.


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    courses = models.ManyToManyField("courses.Course", related_name="assignments")


class AssignmentInstance(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer = models.CharField()
    submitted = models.BooleanField(default=False)
