from courses.models import Course
from questions.models import Question
from rest_framework.test import APITestCase
from users.models import CustomUser

from assignments.models import Assignment, AssignmentTemplate


class AssignmentTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123", user_type=2)
        self.client.force_authenticate(user=self.user)

    def test_get_assignment_detail(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        assignment = Assignment.objects.create(
            name="Sample Assignment",
            due_date="2025-12-01T23:59:00Z",
            timed=True,
            time_limit=1800,
            teacher=self.user,
            course=course,
        )
        url = f"/assignments/{assignment.id}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], assignment.id)
        self.assertEqual(response.data["name"], "Sample Assignment")
        self.assertEqual(response.data["due_date"], "2025-12-01T23:59:00Z")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 1800)
        self.assertEqual(response.data["teacher"], self.user.id)
        self.assertEqual(response.data["course"], course.id)

    def test_get_assignments(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        Assignment.objects.create(
            name="Sample Assignment 1",
            due_date="2025-12-01T23:59:00Z",
            timed=True,
            time_limit=1800,
            teacher=self.user,
            course=course,
        )
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

    # test 2
    def test_create_assignment(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
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
        )
        course.teachers.add(self.user)
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

    def test_delete_assignment(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        assignment = Assignment.objects.create(
            name="To Be Deleted",
            due_date="2025-12-01T23:59:00Z",
            timed=False,
            time_limit=0,
            teacher=self.user,
            course=course,
        )
        url = f"/assignments/{assignment.id}/"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Assignment.objects.filter(id=assignment.id).exists())


class AssignmentTemplateTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass123", user_type=2)
        self.client.force_authenticate(user=self.user)

    def test_get_assignment_template_detail(self):
        template = AssignmentTemplate.objects.create(
            name="Sample Template",
            timed=True,
            time_limit=1200,
            teacher=self.user,
        )
        url = f"/assignment-templates/{template.id}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], template.id)
        self.assertEqual(response.data["name"], "Sample Template")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 1200)
        self.assertEqual(response.data["teacher"], self.user.id)

    def test_get_assignment_templates(self):
        AssignmentTemplate.objects.create(
            name="Sample Template 1",
            timed=False,
            time_limit=0,
            teacher=self.user,
        )
        url = "/assignment-templates/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 0)
        for template in response.data:
            self.assertIn("id", template)
            self.assertIn("name", template)
            self.assertIn("timed", template)
            self.assertIn("time_limit", template)
            self.assertIn("teacher", template)

    def test_create_assignment_template(self):
        url = "/assignment-templates/"
        data = {
            "name": "New Template",
            "timed": True,
            "time_limit": 1500,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Template")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 1500)
        self.assertEqual(response.data["teacher"], self.user.id)

    def test_update_assignment_template(self):
        template = AssignmentTemplate.objects.create(
            name="Old Template",
            timed=False,
            time_limit=0,
            teacher=self.user,
        )
        url = f"/assignment-templates/{template.id}/"
        data = {
            "name": "Updated Template",
            "timed": True,
            "time_limit": 900,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Template")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 900)

    def test_delete_assignment_template(self):
        template = AssignmentTemplate.objects.create(
            name="To Be Deleted",
            timed=False,
            time_limit=0,
            teacher=self.user,
        )
        url = f"/assignment-templates/{template.id}/"
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AssignmentTemplate.objects.filter(id=template.id).exists())

    def test_assign_assignment_template(self):
        course = Course.objects.create(
            name="Sample Course",
            period="1",
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        template = AssignmentTemplate.objects.create(
            name="Template to Assign",
            timed=True,
            time_limit=1800,
            teacher=self.user,
        )
        url = f"/assignment-templates/{template.id}/assign/"
        data = {"course": course.id, "due_date": "2025-12-20T23:59:00Z"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Template to Assign")
        self.assertEqual(response.data["due_date"], "2025-12-20T23:59:00Z")
        self.assertEqual(response.data["timed"], True)
        self.assertEqual(response.data["time_limit"], 1800)
        self.assertEqual(response.data["teacher"], self.user.id)
        self.assertEqual(response.data["course"], course.id)
