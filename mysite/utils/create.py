from assignments.models import Assignment, AssignmentInstance
from questions.models import QuestionInstance


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
