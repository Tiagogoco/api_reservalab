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
    filterset_fields = ["status", "equipment", "user", "loan_date"]
    search_fields = ["equipment__name"]

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-loan_date")
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == models.User.UserRole.STUDENT:
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
        if request_user.role == models.User.UserRole.STUDENT:
            target_user = request_user
        equipment = serializer.validated_data["equipment"]
        quantity = serializer.validated_data["quantity"]
        loan_date = serializer.validated_data["loan_date"]
        due_date = serializer.validated_data["due_date"]
        self._validate_new_loan(equipment, quantity, loan_date, due_date)
        serializer.save(user=target_user)

    def perform_update(self, serializer):
        instance = serializer.instance
        equipment = serializer.validated_data.get("equipment", instance.equipment)
        quantity = serializer.validated_data.get("quantity", instance.quantity)
        loan_date = serializer.validated_data.get("loan_date", instance.loan_date)
        due_date = serializer.validated_data.get("due_date", instance.due_date)
        self._validate_new_loan(equipment, quantity, loan_date, due_date)
        serializer.save()

    def _validate_new_loan(self, equipment, quantity, loan_date, due_date):
        if quantity <= 0:
            raise ValidationError({"quantity": "La cantidad debe ser mayor que cero."})
        if loan_date > due_date:
            raise ValidationError({"due_date": "La fecha de devolución debe ser posterior."})
        if equipment.status != models.Equipment.EquipmentStatus.AVAILABLE:
            raise ValidationError({"equipment": "El equipo no está disponible."})
        if equipment.available_quantity < quantity:
            raise ValidationError({"quantity": "Cantidad solicitada supera disponibilidad."})

    def _ensure_pending(self, loan):
        if loan.status != models.Loan.LoanStatus.PENDING:
            raise ValidationError("Solo se pueden procesar préstamos pendientes.")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        loan = self.get_object()
        self._ensure_pending(loan)
        equipment = loan.equipment
        if equipment.available_quantity < loan.quantity:
            raise ValidationError({"detail": "No hay unidades suficientes para aprobar."})
        equipment.available_quantity -= loan.quantity
        equipment.save(update_fields=["available_quantity", "updated_at"])
        loan.status = models.Loan.LoanStatus.APPROVED
        loan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        loan = self.get_object()
        self._ensure_pending(loan)
        loan.status = models.Loan.LoanStatus.REJECTED
        loan.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(loan).data)

    @action(detail=True, methods=["post"], url_path="return")
    def return_item(self, request, pk=None):
        loan = self.get_object()
        if loan.status not in {
            models.Loan.LoanStatus.APPROVED,
        }:
            raise ValidationError("Solo se pueden devolver préstamos aprobados.")
        damaged = bool(request.data.get("damaged", False))
        loan.return_date = timezone.localdate()
        loan.damaged = damaged
        if damaged:
            loan.status = models.Loan.LoanStatus.DAMAGED
            loan.equipment.status = models.Equipment.EquipmentStatus.MAINTENANCE
            loan.equipment.save(update_fields=["status", "updated_at"])
        else:
            loan.status = models.Loan.LoanStatus.RETURNED
            equipment = loan.equipment
            equipment.available_quantity = min(
                equipment.total_quantity,
                equipment.available_quantity + loan.quantity,
            )
            equipment.save(update_fields=["available_quantity", "updated_at"])
        loan.save(update_fields=["status", "return_date", "damaged", "updated_at"])
        return Response(self.get_serializer(loan).data)
