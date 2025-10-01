from users.models import CustomUser
from questions.models import Question
from assignments.models import Assignment, AssignmentInstance
from courses.models import Course
from .utils import run_django_command
from utils.create import assign_assignment


def run():
    run_django_command("flush --no-input")
    print("\nCreating test data...")
    students_to_create = [
        CustomUser(email=f"student{i}@example.com", user_type=0, password="student")
        for i in range(5)
    ]
    students = CustomUser.objects.bulk_create(students_to_create)
    teachers_to_create = [
        CustomUser(email=f"teacher{i}@example.com", user_type=1, password="teacher")
        for i in range(5)
    ]
    teachers = CustomUser.objects.bulk_create(teachers_to_create)

    admin = CustomUser.objects.create_user(
        email="admin@example.com", password="admin", user_type=2
    )
    superuser = CustomUser.objects.create_superuser(
        email="superuser@example.com", password="superuser"
    )
    question = Question.objects.create(
        title="Test Question",
        question_type="MCQ",
        author=teachers[0],
    )
    assignment = Assignment.objects.create(
        title="Test Assignment",
        due_date="2025-10-15T23:59:00Z",
        teacher=teachers[0],
        timed=True,
        time_limit=3600,
    )
    assignment.questions.add(question)
    course = Course.objects.create(
        title="Test Course",
        description="This is a test course",
        teacher=teachers[0],
    )
    students[0].courses.add(course)
    assign_assignment(assignment, course)
    print("Test data created successfully.")
