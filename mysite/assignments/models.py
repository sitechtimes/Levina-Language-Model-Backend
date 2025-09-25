from django.db import models
from users.models import CustomUser

# Create your models here.


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    due_date = models.DateField()


class AssignmentInstance(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
