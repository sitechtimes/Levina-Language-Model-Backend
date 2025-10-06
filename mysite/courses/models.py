from django.db import models
from users.models import CustomUser

# Create your models here.


class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    students = models.ManyToManyField(CustomUser, related_name="courses")
    assignments = models.ManyToManyField(
        "assignments.Assignment", related_name="courses"
    )
    join_code = models.CharField(max_length=6)
