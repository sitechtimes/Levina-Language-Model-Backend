from users.models import CustomUser
from questions.models import Question
from assignments.models import AssignmentTemplate, AssignmentInstance
from courses.models import Course
from .utils import run_django_command
from utils.create import assign_assignment


def run():
    run_django_command("flush --noinput")
    print("\nCreating test data...")
    student1 = CustomUser.objects.create_user(
        email="student1@example.com",
        password="student",
        user_type=0,
        first_name="Student",
        last_name="One",
    )
    student2 = CustomUser.objects.create_user(
        email="student2@example.com",
        password="student",
        user_type=0,
        first_name="Student",
        last_name="Two",
    )
    sam = CustomUser.objects.create_user(
        email="sam.kipnis@gmail.com",
        password="student",
        user_type=0,
        first_name="Sam",
        last_name="Kipnis",
    )
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com",
        password="teacher",
        user_type=1,
        first_name="Teacher",
        last_name="User",
    )
    admin = CustomUser.objects.create_user(
        email="admin@example.com",
        password="admin",
        user_type=2,
        first_name="Admin",
        last_name="User",
    )
    superuser = CustomUser.objects.create_superuser(
        email="superuser@example.com",
        password="superuser",
        first_name="Super",
        last_name="User",
    )
    question = Question.objects.create(
        title="Test Question",
        question_type="MCQ",
        author=teacher,
    )
    assignment_template = AssignmentTemplate.objects.create(
        title="Test Assignment",
        teacher=teacher,
        timed=True,
        time_limit=3600,
    )
    assignment_template.questions.add(question)
    course = Course.objects.create(
        title="Test Course",
        description="This is a test course",
        period=1,
        class_type="FR",
        teacher=teacher,
    )
    course.students.add(student1, student2, sam)
    assign_assignment(assignment_template, course, due_date="2025-12-15T23:59:00Z")
    print("Test data created successfully.")
