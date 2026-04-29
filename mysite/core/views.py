from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics
from rest_framework.response import Response


class PasswordResetView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"}, status=404
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"http://localhost:8000/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email=None,
            recipient_list=[email],
        )

        return Response({"message": "Password reset link sent."})


class PasswordResetConfirmView(generics.GenericAPIView):
    def get(self, request):
        return Response({"message": "Password reset link sent."})
