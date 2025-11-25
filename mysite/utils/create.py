from assignments.models import (
    AssignmentTemplate,
    AssignmentInstance,
    Session,
    SessionInstance,
    Assignment,
)
from questions.models import QuestionInstance, SessionQuestionInstance
from django.utils import timezone
import hashlib


def assign_assignment(assignment_template, course, due_date=None):
    assignment = Assignment.objects.create(
        course=course,
        assignment_template=assignment_template,
        name=assignment_template.name,
        due_date=due_date,
        timed=assignment_template.timed,
        time_limit=assignment_template.time_limit,
        teacher=assignment_template.teacher,
        date_assigned=timezone.now(),
    )
    assignment.questions.set(assignment_template.questions.all())
    assignment_instances = [
        AssignmentInstance(
            assignment=assignment,
            student=student,
        )
        for student in course.students.all()
    ]
    AssignmentInstance.objects.bulk_create(assignment_instances)
    question_instances = [
        QuestionInstance(assignment_instance=instance, question=question)
        for instance in assignment_instances
        for question in assignment_template.questions.all()
    ]
    QuestionInstance.objects.bulk_create(question_instances)
    return assignment


def join_session(session, student_name):
    session_instance = SessionInstance.objects.create(
        session=session, student_name=student_name
    )
    session_question_instances = [
        SessionQuestionInstance(session_instance=session_instance, question=question)
        for question in session.assignment_template.questions.all()
    ]
    SessionQuestionInstance.objects.bulk_create(session_question_instances)
    token_string = f"token_{session_instance.id}"
    token = hashlib.sha256(token_string.encode()).hexdigest()
    session_instance.token = token
    session_instance.save()
    return session_instance, token


def join_course(course, student):
    course.students.add(student)
    course.save()
    for assignment in course.assignments.all():
        assignment_instance = AssignmentInstance.objects.create(
            assignment=assignment,
            student=student,
        )
        question_instances = [
            QuestionInstance(assignment_instance=assignment_instance, question=question)
            for question in assignment.questions.all()
        ]
        QuestionInstance.objects.bulk_create(question_instances)
