from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from sistema_buap_api import models, permissions as custom_permissions, serializers


class LoanViewSet(viewsets.ModelViewSet):
    queryset = models.Loan.objects.select_related("equipment", "user").all()
    serializer_class = serializers.LoanSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["status", "equipment", "user", "fechaPrestamo"]
    search_fields = ["equipment__name"]

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
        equipment = serializer.validated_data["equipment"]
        quantity = serializer.validated_data["cantidad"]
        fechaPrestamo = serializer.validated_data["fechaPrestamo"]
        fechaDevolucion = serializer.validated_data["fechaDevolucion"]
        self._validate_new_loan(equipment, quantity, fechaPrestamo, fechaDevolucion)
        serializer.save(user=target_user)

    def perform_update(self, serializer):
        instance = serializer.instance
        equipment = serializer.validated_data.get("equipment", instance.equipment)
        quantity = serializer.validated_data.get("cantidad", instance.cantidad)
        fechaPrestamo = serializer.validated_data.get("fechaPrestamo", instance.fechaPrestamo)
        fechaDevolucion = serializer.validated_data.get("fechaDevolucion", instance.fechaDevolucion)
        self._validate_new_loan(equipment, quantity, fechaPrestamo, fechaDevolucion)
        serializer.save()

    def _validate_new_loan(self, equipment, quantity, fechaPrestamo, fechaDevolucion):
        if quantity <= 0:
            raise ValidationError({"quantity": "La cantidad debe ser mayor que cero."})
        if fechaPrestamo > fechaDevolucion:
            raise ValidationError({"due_date": "La fecha de devolución debe ser posterior."})
        if equipment.status != models.Equipment.EquipmentStatus.DISPONIBLE:
            raise ValidationError({"equipment": "El equipo no está disponible."})
        if equipment.cantidadDisponible < quantity:
            raise ValidationError({"quantity": "Cantidad solicitada supera disponibilidad."})

    def _ensure_pending(self, loan):
        if loan.status != models.Loan.LoanStatus.PENDIENTE:
            raise ValidationError("Solo se pueden procesar préstamos pendientes.")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        loan = self.get_object()
        self._ensure_pending(loan)
        equipment = loan.equipment
        if equipment.cantidadDisponible < loan.cantidad:
            raise ValidationError({"detail": "No hay unidades suficientes para aprobar."})
        equipment.cantidadDisponible -= loan.cantidad
        equipment.save(update_fields=["cantidadDisponible", "updated_at"])
        loan.status = models.Loan.LoanStatus.APROBADO
        loan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        loan = self.get_object()
        self._ensure_pending(loan)
        loan.status = models.Loan.LoanStatus.RECHAZADO
        loan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=["post"], url_path="return")
    def return_item(self, request, pk=None):
        loan = self.get_object()
        if loan.status not in {
            models.Loan.LoanStatus.APROBADO,
        }:
            raise ValidationError("Solo se pueden devolver préstamos aprobados.")
        damaged = bool(request.data.get("damaged", False))
        loan.fechaEntrega = timezone.localdate()
        loan.danado = damaged
        if damaged:
            loan.status = models.Loan.LoanStatus.DANADO
            loan.equipo.status = models.Equipment.EquipmentStatus.MANTENIMIENTO
            loan.equipo.save(update_fields=["status", "updated_at"])
        else:
            loan.status = models.Loan.LoanStatus.DEVUELTO
            equipment = loan.equipo
            equipment.cantidadDisponible = min(
                equipment.cantidadTotal,
                equipment.cantidadDisponible + loan.cantidad,
            )
            equipment.save(update_fields=["cantidadDisponible", "updated_at"])
        loan.save(update_fields=["status", "fechaEntrega", "danado", "updated_at"])
        return Response(self.get_serializer(loan).data)
