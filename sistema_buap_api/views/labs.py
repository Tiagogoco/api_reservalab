from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from sistema_buap_api import models, permissions as custom_permissions, serializers


class LabViewSet(viewsets.ModelViewSet):
    queryset = models.Lab.objects.all().order_by("name")
    serializer_class = serializers.LabSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "building"]
    filterset_fields = ["status", "type"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        print(f"🔍 Intento de crear lab - Usuario: {request.user.email}, Rol: {request.user.role}")
        print(f"🔍 Datos recibidos: {request.data}")
        return super().create(request, *args, **kwargs)
