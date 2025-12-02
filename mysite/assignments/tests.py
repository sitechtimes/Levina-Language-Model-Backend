from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser


class AssignmentTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
