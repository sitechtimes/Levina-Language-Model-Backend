from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from courses.models import Course
from questions.models import Question
from assignments.models import Assignment


class AssignmentTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123", user_type=2
        )
        self.client.force_authenticate(user=self.user)

    def test_get_assignments(self):
        url = "/assignments/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 0)
        for assignment in response.data:
            self.assertIn("id", assignment)
            self.assertIn("name", assignment)
            self.assertIn("due_date", assignment)
            self.assertIn("timed", assignment)
            self.assertIn("time_limit", assignment)
            self.assertIn("teacher", assignment)
            self.assertIn("course", assignment)
            self.assertIn("date_assigned", assignment)
            self.assertIn("is_active", assignment)
            self.assertIn("questions", assignment)

    # test
    def test_create_assignment(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
            teacher=self.user,
        )
        question = Question.objects.create(
            name="Sample Question",
            question_type="MCQ",
            author=self.user,
        )
        url = "/assignments/"
        data = {
            "name": "the name",
            "timed": True,
            "time_limit": 3600,
            "questions": [question.id],
            "due_date": "2025-12-15T23:59:00Z",
            "course": course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "the name")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 3600)
        self.assertEqual(response.data["due_date"], "2025-12-15T23:59:00Z")
        self.assertEqual(response.data["course"], course.id)
        self.assertEqual(len(response.data["questions"]), 1)
        self.assertEqual(response.data["questions"][0]["id"], question.id)

    def test_update_assignment(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
            teacher=self.user,
        )
        assignment = Assignment.objects.create(
            name="Old Name",
            due_date="2025-12-01T23:59:00Z",
            timed=False,
            time_limit=0,
            teacher=self.user,
            course=course,
        )
        url = f"/assignments/{assignment.id}/"
        data = {
            "name": "New Name",
            "due_date": "2025-12-31T23:59:00Z",
            "timed": True,
            "time_limit": 1800,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "New Name")
        self.assertEqual(response.data["due_date"], "2025-12-31T23:59:00Z")
        self.assertEqual(response.data["time_limit"], 1800)
