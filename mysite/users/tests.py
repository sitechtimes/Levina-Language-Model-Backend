from rest_framework import status
from rest_framework.test import APITestCase


class PasswordResetConfirmValidationTests(APITestCase):
    def test_confirm_rejects_codes_over_32_characters(self):
        response = self.client.post(
            "/password-reset/confirm/",
            {"code": "a" * 33, "new_password": "new-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)


class PasswordResetConfirmThrottleTests(APITestCase):
    def test_confirm_endpoint_limits_requests(self):
        self.client.defaults["REMOTE_ADDR"] = "192.0.2.1"
        endpoint = "/password-reset/confirm/"

        for _ in range(5):
            response = self.client.post(endpoint, {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(endpoint, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
