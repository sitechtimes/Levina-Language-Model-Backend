from rest_framework.permissions import BasePermission


def has_user_type(user, user_type):
    return user.user_type >= user_type


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, 0)


class IsStudentAndOwnsObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_user_type(request.user, 0) and obj.student == request.user


class IsStudentAndOwnsAssignmentInstance(BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_user_type(request.user, 0) and obj.assignment_instance.student == request.user


class IsStudentAndIsInCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_user_type(request.user, 0) and request.user in obj.students.all()


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, 1)


class IsTeacherAndOwnsObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_user_type(request.user, 1) and request.user in obj.teachers.all()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, 2)
