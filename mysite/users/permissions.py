from rest_framework.permissions import BasePermission


class StudentPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 0


class TeacherPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 1


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 2


class SuperuserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 3
