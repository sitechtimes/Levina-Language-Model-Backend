from rest_framework.permissions import BasePermission


def has_user_type(user, user_type):
    return user.is_authenticated and int(user.user_type) >= int(user_type)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, "0")


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, "1")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return has_user_type(request.user, "2")


class IsSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class OwnsQuestionInstance(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assignment_instance.student == request.user
