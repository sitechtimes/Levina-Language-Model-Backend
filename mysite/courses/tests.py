from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import CustomUser
from courses.models import Course
from questions.models import Question
from assignments.models import Assignment


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="testpass123", user_type=2
        )
        self.client.force_authenticate(user=self.user)

    def test_get_course_detail(self):
        course = Course.objects.create(
            name="Sample Course",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        url = f"/courses/{course.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], course.id)
        self.assertEqual(response.data["name"], "Sample Course")
        self.assertEqual(response.data["period"], 1)
        self.assertEqual(response.data["class_type"], "Freshman Russian")
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertEqual(response.data["teachers"][0]["id"], self.user.id)

    def test_get_courses_list(self):
        course1 = Course.objects.create(
            name="Course One",
            period=1,
            class_type="Freshman Russian",
        )
        course1.teachers.add(self.user)
        course2 = Course.objects.create(
            name="Course Two",
            period=2,
            class_type="Sophomore Spanish",
        )
        course2.teachers.add(self.user)

        url = "/courses/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        for course in response.data:
            self.assertIn("id", course)
            self.assertIn("name", course)
            self.assertIn("period", course)
            self.assertIn("class_type", course)
            self.assertIn("teachers", course)
            self.assertEqual(len(course["teachers"]), 1)
            self.assertEqual(course["teachers"][0]["id"], self.user.id)

    def test_create_course(self):
        url = "/courses/"
        data = {
            "name": "New Course",
            "period": 3,
            "class_type": "Freshman Russian",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Course")
        self.assertEqual(response.data["period"], 3)
        self.assertEqual(response.data["class_type"], "Freshman Russian")
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertEqual(response.data["teachers"][0]["id"], self.user.id)

    def test_update_course(self):
        course = Course.objects.create(
            name="Old Course",
            period=2,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        url = f"/courses/{course.id}/"
        data = {
            "name": "Updated Course",
            "period": 4,
            "class_type": "Russian in Business",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Course")
        self.assertEqual(response.data["period"], 4)
        self.assertEqual(response.data["class_type"], "Russian in Business")
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertEqual(response.data["teachers"][0]["id"], self.user.id)

    def test_delete_course(self):
        course = Course.objects.create(
            name="Course to Delete",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        url = f"/courses/{course.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    def test_generate_join_code(self):
        course = Course.objects.create(
            name="Code Course",
            period=2,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        url = f"/courses/{course.id}/new_join_code/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_join_course(self):
        student = CustomUser.objects.create_user(
            email="test2@example.com", password="testpass123", user_type=0
        )
        self.client.force_authenticate(user=student)
        course = Course.objects.create(
            name="Joinable Course",
            period=2,
            class_type="Freshman Russian",
        )
        course.join_code = "abcdef"
        course.save()
        data = {"join_code": "abcdef"}
        url = f"/courses/{course.id}/join/"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(student, course.students.all())

    def test_get_course_assignments(self):
        course = Course.objects.create(
            name="Assignment Course",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        assignment1 = Assignment.objects.create(
            name="Assignment One",
            due_date="2025-12-01T23:59:00Z",
            timed=True,
            time_limit=60,
            teacher=self.user,
            course=course,
        )
        assignment2 = Assignment.objects.create(
            name="Assignment Two",
            due_date="2025-12-15T23:59:00Z",
            timed=False,
            time_limit=0,
            teacher=self.user,
            course=course,
        )
        url = f"/courses/{course.id}/assignments/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        for assignment in response.data:
            self.assertIn("id", assignment)
            self.assertIn("name", assignment)
            self.assertIn("due_date", assignment)
            self.assertEqual(assignment["course"], course.id)
            self.assertIn("timed", assignment)
            self.assertIn("time_limit", assignment)

    def test_get_course_students(self):
        course = Course.objects.create(
            name="Student Course",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        student1 = CustomUser.objects.create_user(
            email="student1@example.com", password="student", user_type=0
        )
        student2 = CustomUser.objects.create_user(
            email="student2@example.com", password="student", user_type=0
        )
        course.students.add(student1)
        course.students.add(student2)
        url = f"/courses/{course.id}/students/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_update_teachers(self):
        course = Course.objects.create(
            name="Teacher Update Course",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        new_teacher = CustomUser.objects.create_user(
            email="new_teacher@example.com", password="teacher", user_type=1
        )
        url = f"/courses/{course.id}/update_teachers/"
        data = {"teachers": [new_teacher.id]}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertIn(new_teacher, course.teachers.all())

    def test_remove_student(self):
        course = Course.objects.create(
            name="Remove Student Course",
            period=1,
            class_type="Freshman Russian",
        )
        course.teachers.add(self.user)
        student = CustomUser.objects.create_user(
            email="student@example.com", password="student", user_type=0
        )
        course.students.add(student)
        url = f"/courses/{course.id}/remove_student/"
        data = {"student": student.id}
        response = self.client.delete(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(student, course.students.all())
