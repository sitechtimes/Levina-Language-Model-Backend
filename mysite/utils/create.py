from assignments.models import Assignment, AssignmentInstance, Session, SessionInstance
from questions.models import QuestionInstance, SessionQuestionInstance
import hashlib


def assign_assignment(assignment, course):
    course.assignments.add(assignment)
    assignment_instances = [
        AssignmentInstance(
            assignment=assignment,
            student=student,
        )
        for student in course.students.all()
    ]
    AssignmentInstance.objects.bulk_create(assignment_instances)
    question_instances = [
        QuestionInstance(assignment_instance=assignment_instance, question=question)
        for question in assignment.questions.all()
        for assignment_instance in assignment_instances
    ]
    QuestionInstance.objects.bulk_create(question_instances)


def join_session(session, student_name):
    session_instance = SessionInstance.objects.create(
        session=session, student_name=student_name
    )
    session_question_instances = [
        SessionQuestionInstance(session_instance=session_instance, question=question)
        for question in session.assignment.questions.all()
    ]
    SessionQuestionInstance.objects.bulk_create(session_question_instances)
    token_string = f"token_{session_instance.id}"
    token = hashlib.sha256(token_string.encode()).hexdigest()
    session_instance.token = token
    session_instance.save()
    return session_instance, token
