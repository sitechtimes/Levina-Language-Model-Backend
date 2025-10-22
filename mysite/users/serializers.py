from rest_framework import serializers
from .models import CustomUser, PasswordResetCode
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from utils.random import random_numeric


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.get(email=validated_data["email"])
        code = random_numeric(6)
        PasswordResetCode.objects.create(user=user, code=code)
        send_mail(
            subject="Your Password Reset Code",
            message=f"Your password reset code is: {code}\nIt expires in 10 minutes.",
            from_email="no-reply@example.com",
            recipient_list=user.email,
            fail_silently=False,
        )
        return Response({"message": "Password reset code sent to email."}, status=200)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data.get("email"))
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        try:
            reset_code = PasswordResetCode.objects.filter(
                user=user, code=data.get("code"), is_used=False
            ).latest("created_at")
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used code.")

        if reset_code.is_expired():
            raise serializers.ValidationError("Code expired.")

        data["user"] = user
        data["reset_code"] = reset_code
        return data
