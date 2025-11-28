from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from sistema_buap_api import models, permissions as custom_permissions, serializers


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = models.Reservation.objects.select_related("lab", "user").all()
    serializer_class = serializers.ReservationSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["status", "lab", "user", "fecha"]
    search_fields = ["motivo"]

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-fecha", "-horaInicio")
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == models.User.UserRole.ESTUDIANTE:
            queryset = queryset.filter(user=user)
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        params = self.request.query_params
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        if date_from:
            try:
                parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
                queryset = queryset.filter(fecha__gte=parsed)
            except ValueError:
                raise ValidationError({"date_to": "Formato inválido. Use YYYY-MM-DD."})
        if date_to:
            try:
                parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
                queryset = queryset.filter(fecha__lte=parsed)
            except ValueError:
                raise ValidationError({"date_to": "Formato inválido. Use YYYY-MM-DD."})
        return queryset

    def get_permissions(self):
        if self.action in {"approve", "reject"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        if self.action in {"destroy", "update", "partial_update"}:
            permission_classes = [custom_permissions.IsAdminOrTech]
        elif self.action == "cancel":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        print(f"🔍 Datos de reserva recibidos: {self.request.data}")
        print(f"🔍 Usuario: {self.request.user}")
        request_user = self.request.user
        target_user = serializer.validated_data.get("user", request_user)
        if request_user.role == models.User.UserRole.ESTUDIANTE:
            target_user = request_user
        self._validate_reservation(
            instance=None,
            lab=serializer.validated_data["lab"],
            fecha=serializer.validated_data["fecha"],
            horaInicio=serializer.validated_data["horaInicio"],
            horaFin=serializer.validated_data["horaFin"],
        )
        serializer.save(user=target_user)

    def perform_update(self, serializer):
        instance = serializer.instance
        validated = serializer.validated_data
        lab = validated.get("lab", instance.lab)
        fecha = validated.get("fecha", instance.fecha)
        horaInicio = validated.get("horaInicio", instance.horaInicio)
        horaFin = validated.get("horaFin", instance.horaFin)
        self._validate_reservation(
            instance=instance,
            lab=lab,
            fecha=fecha,
            horaInicio=horaInicio,
            horaFin=horaFin,
        )
        serializer.save()

    def _validate_reservation(self, *, instance, lab, fecha, horaInicio, horaFin):
        if lab.status != models.Lab.LabStatus.ACTIVO:
            raise ValidationError({"lab": "El laboratorio no está disponible."})
        if fecha < timezone.localdate():
            raise ValidationError({"fecha": "No se puede reservar con fecha pasada."})
        overlaps = models.Reservation.objects.filter(
            lab=lab,
            fecha=fecha,
            status__in=[
                models.Reservation.ReservationStatus.PENDIENTE,
                models.Reservation.ReservationStatus.APROBADO,
            ],
        )
        if instance is not None:
            overlaps = overlaps.exclude(pk=instance.pk)
        overlaps = overlaps.filter(
            Q(horaInicio__lt=horaFin) & Q(horaFin__gt=horaInicio)
        )
        if overlaps.exists():
            raise ValidationError("El laboratorio ya está reservado en ese horario.")

    def _set_status(self, reservation, status_value):
        reservation.status = status_value
        reservation.save(update_fields=["status", "updated_at"])
        return reservation

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        reservation = self.get_object()
        self._set_status(reservation, models.Reservation.ReservationStatus.APROBADO)
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        reservation = self.get_object()
        self._set_status(reservation, models.Reservation.ReservationStatus.RECHAZADO)
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        user = request.user
        if user.role == models.User.UserRole.ESTUDIANTE and reservation.user_id != user.id:
            return Response({"detail": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)
        reason = request.data.get("reason", "")
        reservation.cancel_reason = reason
        self._set_status(reservation, models.Reservation.ReservationStatus.CANCELADO)
        reservation.save(update_fields=["cancel_reason", "status", "updated_at"])
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)