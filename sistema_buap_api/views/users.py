from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from sistema_buap_api import models, permissions as custom_permissions, serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all().order_by("id")
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "email", "matricula"]
    filterset_fields = ["role"]

    def get_permissions(self):
        if self.action in {"list", "retrieve", "create", "update", "partial_update", "destroy"}:
            permission_classes = [custom_permissions.IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.UserRegistrationSerializer
        return serializers.UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user:
            return Response({"detail": "No puedes eliminar tu propio usuario."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
