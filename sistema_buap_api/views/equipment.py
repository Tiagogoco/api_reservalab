from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from sistema_buap_api import models, permissions as custom_permissions, serializers


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = models.Equipment.objects.select_related("lab").all().order_by("name")
    serializer_class = serializers.EquipmentSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "inventory_number"]
    filterset_fields = ["status", "lab"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.available_quantity > instance.total_quantity:
            instance.available_quantity = instance.total_quantity
            instance.save(update_fields=["available_quantity"])
