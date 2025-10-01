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
    question_instances = [QuestionInstance()]
