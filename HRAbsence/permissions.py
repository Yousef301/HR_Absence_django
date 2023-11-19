from .models import session, UserAlchemy

from rest_framework import permissions


# class ManagerPermissions(permissions.BasePermission):
#     message = "You don't have permission..."
#
#     def has_permission(self, request, view):
#         usr = session.query(UserAlchemy.role).filter(UserAlchemy.id == request.user.user_id).first()
#         manager = bool(usr.role.name == "Manager")
#         return bool(request.user and manager)


class ManagerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
