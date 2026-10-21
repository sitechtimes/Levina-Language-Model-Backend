from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser

from questions.views import MAX_AUDIO_UPLOAD_SIZE, validate_audio_upload


class AudioUploadValidationTests(APITestCase):
    def test_dialogue_create_rejects_spoofed_mime_type(self):
        teacher = CustomUser.objects.create_user(
            email="upload-teacher@example.com",
            password="password",
            user_type=1,
        )
        self.client.force_authenticate(user=teacher)
        upload = SimpleUploadedFile("voice.m4a", b"not audio", content_type="audio/mp4")

        response = self.client.post(
            "/dialogues/",
            {
                "initial_statement": upload,
                "description": "Test dialogue",
                "max_statements": 3,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valid MP4 audio file", response.data["error"])

    def test_rejects_file_with_spoofed_audio_mime_type(self):
        upload = SimpleUploadedFile("voice.m4a", b"not audio", content_type="audio/mp4")

        with patch("questions.views.magic.from_buffer", return_value="text/plain"):
            response = validate_audio_upload(upload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valid MP4 audio file", response.data["error"])

    def test_rejects_upload_over_10_mib_without_inspecting_contents(self):
        upload = SimpleUploadedFile(
            "voice.m4a",
            b"x" * (MAX_AUDIO_UPLOAD_SIZE + 1),
            content_type="audio/mp4",
        )

        with patch("questions.views.magic.from_buffer") as detect_type:
            response = validate_audio_upload(upload)

        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        detect_type.assert_not_called()

    def test_accepts_m4a_detected_from_file_contents(self):
        upload = SimpleUploadedFile("voice.m4a", b"audio contents", content_type="text/plain")

        with patch("questions.views.magic.from_buffer", return_value="audio/x-m4a"):
            response = validate_audio_upload(upload)

        self.assertIsNone(response)
