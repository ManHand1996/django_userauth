"""
restful request permission
"""
from rest_framework.permissions import BasePermission


class ControlManagerPermission(BasePermission):
    """
    权限管理后台管理员权限
    """

    def has_permission(self, request, view):
        """
        后台管理员
        :param request:
        :type request:
        :param view:
        :type view:
        :return:
        :rtype:
        """
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        pass