from .models import BusinessGroup

from rest_framework import permissions


# class ManagerPermissions(permissions.BasePermission):
#     message = "You don't have permission..."
#
#     def has_permission(self, request, view):
#         usr = session.query(UserAlchemy.role).filter(UserAlchemy.id == request.user.user_id).first()
#         manager = bool(usr.role.name == "Manager")
#         return bool(request.user and manager)

# class IsAuthenticated(permissions.BasePermission):
#     def has_permission(self, request, view):
#         u_pk = int(request.parser_context['kwargs']['pk'])
#         return bool(request.user and request.user.is_authenticated and u_pk == request.user.user_id)


class ManagerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        bid = request.parser_context['kwargs']['business_pk']
        group = request.user.groups.filter(name='Manager').first()

        if group:
            return BusinessGroup.objects.filter(group=group.id, business_id=bid).exists()
        return False


class CanView(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('HRAbsence.view_request')


class CanUpdate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("HRAbsence.edit_request")


class CanApprove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("HRAbsence.approve_request")


class CanDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("HRAbsence.delete_request")
