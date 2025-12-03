from rest_framework import permissions

from sistema_buap_api import models


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role == models.User.UserRole.ADMIN


class IsAdminOrTech(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in {
            models.User.UserRole.ADMIN,
            models.User.UserRole.TECNICO,
        }


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == models.User.UserRole.ADMIN:
            return True
        return obj == user
