import calendar
from datetime import datetime

from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from sistema_buap_api import models, permissions as custom_permissions


class BaseReportView(APIView):
    permission_classes = [custom_permissions.IsAdminOrTech]


class OccupancyReportView(BaseReportView):
    def get(self, request, *args, **kwargs):
        period = request.query_params.get("period")
        start_date, end_date, period_label = _parse_period(period)
        reservations = models.Reservation.objects.filter(
            status=models.Reservation.ReservationStatus.APPROVED,
            date__range=(start_date, end_date),
        )
        data = []
        total_days = (end_date - start_date).days + 1
        total_hours_capacity = max(total_days * 12, 1)
        for lab in models.Lab.objects.all():
            lab_reservations = reservations.filter(lab=lab).values(
                "start_time", "end_time"
            )
            reserved_hours = 0
            for item in lab_reservations:
                delta = datetime.combine(datetime.min, item["end_time"]) - datetime.combine(
                    datetime.min, item["start_time"]
                )
                reserved_hours += delta.total_seconds() / 3600
            occupancy_rate = min(reserved_hours / total_hours_capacity, 1)
            data.append(
                {
                    "lab_id": lab.id,
                    "lab_name": lab.name,
                    "period": period_label,
                    "occupancy_rate": round(occupancy_rate, 4),
                }
            )
        return Response(data)


class EquipmentUsageReportView(BaseReportView):
    def get(self, request, *args, **kwargs):
        start_date, end_date = _parse_date_range(request)
        loans = models.Loan.objects.filter(
            status__in=[
                models.Loan.LoanStatus.APPROVED,
                models.Loan.LoanStatus.RETURNED,
                models.Loan.LoanStatus.DAMAGED,
            ],
            loan_date__range=(start_date, end_date),
        )
        aggregated = loans.values("equipment_id", "equipment__name").annotate(total_loans=Count("id"))
        data = [
            {
                "equipment_id": item["equipment_id"],
                "equipment_name": item["equipment__name"],
                "total_loans": item["total_loans"],
            }
            for item in aggregated
        ]
        return Response(data)


class IncidentReportView(BaseReportView):
    def get(self, request, *args, **kwargs):
        start_date, end_date = _parse_date_range(request)
        incidents = models.Loan.objects.filter(
            status=models.Loan.LoanStatus.DAMAGED,
            return_date__range=(start_date, end_date),
        ).select_related("equipment")
        data = [
            {
                "loan_id": loan.id,
                "equipment_name": loan.equipment.name,
                "damage_type": "DAMAGED" if loan.damaged else "RETURNED",
                "reported_at": loan.updated_at.isoformat(),
            }
            for loan in incidents
        ]
        return Response(data)


def _parse_period(period: str | None):
    today = timezone.localdate()
    if not period:
        year, month = today.year, today.month
        period_label = today.strftime("%Y-%m")
    else:
        try:
            parsed = datetime.strptime(period, "%Y-%m")
        except ValueError as exc:
            raise ValidationError({"period": "Formato inválido. Use YYYY-MM."}) from exc
        year, month = parsed.year, parsed.month
        period_label = parsed.strftime("%Y-%m")
    start_day = 1
    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime(year, month, start_day).date()
    end_date = datetime(year, month, last_day).date()
    return start_date, end_date, period_label


def _parse_date_range(request):
    start_param = request.query_params.get("from")
    end_param = request.query_params.get("to")
    today = timezone.localdate()
    try:
        start_date = datetime.strptime(start_param, "%Y-%m-%d").date() if start_param else today.replace(day=1)
        end_date = datetime.strptime(end_param, "%Y-%m-%d").date() if end_param else today
    except ValueError as exc:
        raise ValidationError({"detail": "Fechas inválidas. Use YYYY-MM-DD."}) from exc
    if start_date > end_date:
        raise ValidationError({"detail": "El rango de fechas es inválido."})
    return start_date, end_date
