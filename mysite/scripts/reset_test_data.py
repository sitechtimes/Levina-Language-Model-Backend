from users.models import CustomUser
from questions.models import Question
from assignments.models import Assignment, AssignmentInstance
from courses.models import Course
from .utils import run_django_command


def run():
    run_django_command("flush --no-input")
    print("\nCreating users...")
    student = CustomUser.objects.create_user(
        email="student@example.com", password="student", user_type=0
    )
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="teacher", user_type=1
    )
    admin = CustomUser.objects.create_user(
        email="admin@example.com", password="admin", user_type=2
    )
    superuser = CustomUser.objects.create_superuser(
        email="superuser@example.com", password="superuser"
    )
    question = Question.objects.create(
        title="Test Question",
        question_type="MCQ",
        author=teacher,
    )
    assignment = Assignment.objects.create(
        title="Test Assignment",
        due_date="2025-10-15T23:59:00Z",
        teacher=teacher,
    )
    assignment.questions.add(question)
    course = Course.objects.create(
        title="Test Course",
        description="This is a test course",
        teacher=teacher,
    )
    student.courses.add(course)
    course.assignments.add(assignment)
    assignment_instances = [
        AssignmentInstance(
            assignment=assignment,
            student=student,
        )
        for student in course.students.all()
    ]
    AssignmentInstance.objects.bulk_create(assignment_instances)
    print("Users created successfully.")
