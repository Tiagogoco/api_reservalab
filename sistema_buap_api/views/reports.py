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
        periodo = request.query_params.get("periodo")
        fechaInicio, fechaFin, period_label = _parse_period(periodo)
        reservaciones = models.Reservacion.objects.filter(
            status=models.Reservacion.ReservacionStatus.APROBADO,
            fecha__range=(fechaInicio, fechaFin),
        )
        data = []
        diasTotales = (fechaFin - fechaInicio).days + 1
        capacidad_total_horas = max(diasTotales * 12, 1)
        for lab in models.Lab.objects.all():
            reservacionesLab = reservaciones.filter(lab=lab).values(
                "fechaInicio", "fechaFin"
            )
            horas_reservadas = 0
            for item in reservacionesLab:
                delta = datetime.combine(datetime.min, item["fechaFin"]) - datetime.combine(
                    datetime.min, item["fechaInicio"]
                )
                horas_reservadas += delta.total_seconds() / 3600
            tasa_ocupacion = min(horas_reservadas / capacidad_total_horas, 1)
            data.append(
                {
                    "idLab": lab.id,
                    "nombreLab": lab.name,
                    "periodo": period_label,
                    "tasa_ocupacion": round(tasa_ocupacion, 4),
                }
            )
        return Response(data)


class EquipmentUsageReportView(BaseReportView):
    def get(self, request, *args, **kwargs):
        start_date, end_date = _parse_date_range(request)
        loans = models.Prestamo.objects.filter(
            status__in=[
                models.Prestamo.PrestamoStatus.APROBADO,
                models.Prestamo.PrestamoStatus.DEVUELTO,
                models.Prestamo.PrestamoStatus.DANADO,
            ],
            fechaPrestamo__range=(start_date, end_date),
        )
        aggregated = loans.values("equipo_id", "equipo__nombre").annotate(prestamos_totales=Count("id"))
        data = [
            {
                "equipo_id": item["equipo_id"],
                "equipo_name": item["equipo__nombre"],
                "prestamos_totales": item["prestamos_totales"],
            }
            for item in aggregated
        ]
        return Response(data)


class IncidentReportView(BaseReportView):
    def get(self, request, *args, **kwargs):
        fechaInicio, fechaFin = _parse_date_range(request)
        incidentes = models.Prestamo.objects.filter(
            status=models.Prestamo.PrestamoStatus.DANADO,
            fechaEntrega__range=(fechaInicio, fechaFin),
        ).select_related("equipo")
        data = [
            {
                "loan_id": loan.id,
                "nombre": loan.equipo.nombre,
                "tipo_dano": "DANADO" if loan.danado else "DEVUELTO",
                "reported_at": loan.updated_at.isoformat(),
            }
            for loan in incidentes
        ]
        return Response(data)


def _parse_period(period: str | None):
    hoy = timezone.localdate()
    if not period:
        año, mes = hoy.año, hoy.mes
        period_label = hoy.strftime("%Y-%m")
    else:
        try:
            parsed = datetime.strptime(period, "%Y-%m")
        except ValueError as exc:
            raise ValidationError({"period": "Formato inválido. Use YYYY-MM."}) from exc
        año, mes = parsed.year, parsed.month
        period_label = parsed.strftime("%Y-%m")
    start_day = 1
    ultimo_dia = calendar.monthrange(año, mes)[1]
    fechaInicio = datetime(año, mes, start_day).date()
    fechaFin = datetime(año, mes, ultimo_dia).date()
    return fechaInicio, fechaFin, period_label


def _parse_date_range(request):
    start_param = request.query_params.get("from")
    end_param = request.query_params.get("to")
    today = timezone.localdate()
    try:
        fechaInicio = datetime.strptime(start_param, "%Y-%m-%d").date() if start_param else today.replace(day=1)
        fechaFin = datetime.strptime(end_param, "%Y-%m-%d").date() if end_param else today
    except ValueError as exc:
        raise ValidationError({"detail": "Fechas inválidas. Use YYYY-MM-DD."}) from exc
    if fechaInicio > fechaFin:
        raise ValidationError({"detail": "El rango de fechas es inválido."})
    return fechaInicio, fechaFin