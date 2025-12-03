from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from sistema_buap_api import models, permissions as custom_permissions, serializers


class LoanViewSet(viewsets.ModelViewSet):
    queryset = models.Prestamo.objects.select_related("equipo", "user").all()
    serializer_class = serializers.PrestamoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["status", "equipo", "user", "fechaPrestamo"]
    search_fields = ["equipo__nombre"]
    def get_queryset(self):
        queryset = super().get_queryset().order_by("-fechaPrestamo")
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == models.User.UserRole.ESTUDIANTE:
            queryset = queryset.filter(user=user)
        return queryset

    def get_permissions(self):
        if self.action in {"approve", "reject", "return_item"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        elif self.action in {"update", "partial_update", "destroy"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        request_user = self.request.user
        target_user = serializer.validated_data.get("user", request_user)
        if request_user.role == models.User.UserRole.ESTUDIANTE:
            target_user = request_user
        equipo = serializer.validated_data["equipo"]
        cantidad = serializer.validated_data["cantidad"]
        fechaPrestamo = serializer.validated_data["fechaPrestamo"]
        fechaDevolucion = serializer.validated_data["fechaDevolucion"]
        self._validate_new_loan(equipo, cantidad, fechaPrestamo, fechaDevolucion)
        serializer.save(user=target_user)

    def perform_update(self, serializer):
        instance = serializer.instance
        equipo = serializer.validated_data.get("equipo", instance.equipo)
        cantidad = serializer.validated_data.get("cantidad", instance.cantidad)
        fechaPrestamo = serializer.validated_data.get("fechaPrestamo", instance.fechaPrestamo)
        fechaDevolucion = serializer.validated_data.get("fechaDevolucion", instance.fechaDevolucion)
        self._validate_new_loan(equipo, cantidad, fechaPrestamo, fechaDevolucion)
        serializer.save()

    def _validate_new_loan(self, equipo, cantidad, fechaPrestamo, fechaDevolucion):
        if cantidad <= 0:
            raise ValidationError({"cantidad": "La cantidad debe ser mayor que cero."})
        if fechaPrestamo > fechaDevolucion:
            raise ValidationError({"fechaDevolucion": "La fecha de devolución debe ser posterior."})
        if equipo.status != models.Equipo.EquipoStatus.DISPONIBLE:
            raise ValidationError({"equipo": "El equipo no está disponible."})
        if equipo.cantidadDisponible < cantidad:
            raise ValidationError({"cantidad": "Cantidad solicitada supera disponibilidad."})
    
    def _ensure_pending(self, prestamo):
        if prestamo.status != models.Prestamo.PrestamoStatus.PENDIENTE:
            raise ValidationError("Solo se pueden procesar préstamos pendientes.")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        prestamo = self.get_object()
        self._ensure_pending(prestamo)
        equipo = prestamo.equipo
        if equipo.cantidadDisponible < prestamo.cantidad:
            raise ValidationError({"detail": "No hay unidades suficientes para aprobar."})
        equipo.cantidadDisponible -= prestamo.cantidad
        equipo.save(update_fields=["cantidadDisponible", "updated_at"])
        prestamo.status = models.Prestamo.PrestamoStatus.APROBADO
        prestamo.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(prestamo).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        prestamo = self.get_object()
        self._ensure_pending(prestamo)
        prestamo.status = models.Prestamo.PrestamoStatus.RECHAZADO
        prestamo.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(prestamo).data)
    
    @action(detail=True, methods=["post"], url_path="return")
    def return_item(self, request, pk=None):
        prestamo = self.get_object()
        if prestamo.status not in {
            models.Prestamo.PrestamoStatus.APROBADO,
        }:
            raise ValidationError("Solo se pueden devolver préstamos aprobados.")
        danado = bool(request.data.get("danado", False))
        prestamo.fechaEntrega = timezone.localdate()
        prestamo.danado = danado
        if danado:
            prestamo.status = models.Prestamo.PrestamoStatus.DANADO
            prestamo.equipo.status = models.Equipo.EquipoStatus.MANTENIMIENTO
            prestamo.equipo.save(update_fields=["status", "updated_at"])
        else:
            prestamo.status = models.Prestamo.PrestamoStatus.DEVUELTO
            equipo = prestamo.equipo
            equipo.cantidadDisponible = min(
                equipo.cantidadTotal,
                equipo.cantidadDisponible + prestamo.cantidad,
            )
            equipo.save(update_fields=["cantidadDisponible", "updated_at"])
        prestamo.save(update_fields=["status", "fechaEntrega", "danado", "updated_at"])
        return Response(self.get_serializer(prestamo).data)