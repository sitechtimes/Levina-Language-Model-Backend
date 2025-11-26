from django.db import models
from users.models import CustomUser
from django.utils import timezone
from rest_framework import serializers

# Create your models here.


class ClassTypes(models.TextChoices):
    FR = "Freshman Russian"
    FHR = "Freshman Heritage Russian"
    SR = "Sophomore Russian"
    SAR = "Sophomore Advanced Russian"
    SHR = "Sophomore Heritage Russian"
    JR = "Junior Russian"
    CR = "College Russian"
    RIB = "Russian in Business"
    CHR = "College Heritage Russian"


class Course(models.Model):
    name = models.CharField(max_length=100)
    period = models.IntegerField()
    class_type = models.CharField(choices=ClassTypes.choices)
    teacher = models.ManyToManyField(CustomUser, related_name="courses_teachers")
    students = models.ManyToManyField(CustomUser, related_name="courses_students")
    join_code = models.CharField(max_length=6)
