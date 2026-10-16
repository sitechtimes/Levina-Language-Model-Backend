import hashlib, secrets

from assignments.models import (
    Assignment,
    AssignmentInstance,
    SessionInstance,
)
from django.utils import timezone
from questions.models import (
    DialogueInstance,
    DialogueStatement,
    QuestionInstance,
    SessionDialogueInstance,
    SessionQuestionInstance,
)


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
    dialogue_instances = [
        DialogueInstance(assignment_instance=instance, dialogue=dialogue)
        for instance in assignment_instances
        for dialogue in assignment_template.dialogues.all()
    ]
    DialogueInstance.objects.bulk_create(dialogue_instances)
    initial_statements = [
        DialogueStatement(
            dialogue_instance=dialogue_instance,
            audio=dialogue_instance.dialogue.initial_statement,
            author="AI",
        )
        for dialogue_instance in dialogue_instances
    ]
    DialogueStatement.objects.bulk_create(initial_statements)
    return assignment


def join_session(session, student_name):
    session_instance = SessionInstance.objects.create(session=session, student_name=student_name)
    session_question_instances = [
        SessionQuestionInstance(session_instance=session_instance, question=question)
        for question in session.assignment_template.questions.all()
    ]
    SessionQuestionInstance.objects.bulk_create(session_question_instances)
    session_dialogue_instances = [
        SessionDialogueInstance(session_instance=session_instance, dialogue=dialogue)
        for dialogue in session.assignment_template.dialogues.all()
    ]
    SessionDialogueInstance.objects.bulk_create(session_dialogue_instances)
    token = secrets.token_urlsafe(32)
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
