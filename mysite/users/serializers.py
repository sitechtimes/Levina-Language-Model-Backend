from rest_framework import serializers
from .models import CustomUser, PasswordResetCode
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from utils.random import random_numeric


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "user_type"]
