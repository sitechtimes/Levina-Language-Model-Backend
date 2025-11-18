from django.db import models
from users.models import CustomUser
from django.utils import timezone
from rest_framework import serializers

# Create your models here.


class Course(models.Model):
    CLASS_TYPES = [
        ("FR", "Freshman Russian"),
        ("FHR", "Freshman Heritage Russian"),
        ("SR", "Sophomore Russian"),
        ("SAR", "Sophomore Advanced Russian"),
        ("SHR", "Sophomore Heritage Russian"),
        ("JR", "Junior Russian"),
        ("CR", "College Russian"),
        ("CHR", "College Heritage Russian"),
        ("RIB", "Russian in Business"),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    period = models.IntegerField()
    class_type = models.CharField(max_length=3, choices=CLASS_TYPES)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    students = models.ManyToManyField(CustomUser, related_name="courses")
    join_code = models.CharField(max_length=6)
