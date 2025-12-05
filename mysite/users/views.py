# views.py
import os

from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from utils.random import random_alphanumeric

from .models import CustomUser, PasswordResetCode
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            requested_user = CustomUser.objects.get(email=request.data.get("email"))
        except CustomUser.DoesNotExist:
            return Response({"error": "No account found with this email."}, status=404)
        code = random_alphanumeric(20)
        PasswordResetCode.objects.create(user=requested_user, code=code)
        url = f"{os.getenv('FRONTEND_URL')}/reset-password/confirm?code={code}"
        send_mail(
            subject="Your Password Reset Code",
            message=f"Click this link to reset your password: {url}\nIt expires in 10 minutes.",
            recipient_list=[requested_user.email],
            fail_silently=False,
            from_email=os.getenv("GMAIL"),
        )
        return Response({"message": "Password reset code sent to email."}, status=200)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            reset_code = PasswordResetCode.objects.filter(code=request.data.get("code")).latest("created_at")
        except PasswordResetCode.DoesNotExist:
            return Response({"error": "Invalid code."}, status=400)
        if reset_code.is_used:
            return Response({"error": "Code already used."}, status=400)
        if reset_code.is_expired():
            return Response({"error": "Code expired."}, status=400)
        reset_code.user.set_password(request.data.get("new_password"))
        reset_code.is_used = True
        reset_code.user.save()
        reset_code.save()
        return Response({"message": "Password has been reset successfully."}, status=200)


class GetUserView(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user = CustomUser.objects.get(id=request.user.id)
            return Response(UserSerializer(user).data, status=200)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
