from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from sistema_buap_api.views import auth, bootstrap, equipment, labs, loans, reservations, reports, users

router = DefaultRouter()
router.register("users", users.UserViewSet, basename="user")
router.register("labs", labs.LabViewSet, basename="lab")
router.register("equipment", equipment.EquipmentViewSet, basename="equipment")
router.register("reservations", reservations.ReservationViewSet, basename="reservation")
router.register("loans", loans.LoanViewSet, basename="loan")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("bootstrap/version", bootstrap.VersionView.as_view()),
    # JWT endpoints
    path("api/auth/login/", auth.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/register/", auth.RegisterView.as_view(), name="auth_register"),
    path("api/auth/me/", auth.ProfileView.as_view(), name="auth_profile"),
    # Legacy compatibility
    path("token/", auth.CustomTokenObtainPairView.as_view(), name="token_legacy"),
    path("api/reports/occupancy/", reports.OccupancyReportView.as_view(), name="report_occupancy"),
    path("api/reports/equipment-usage/",reports.EquipmentUsageReportView.as_view(), name="report_equipment_usage",),
    path("api/reports/incidents/",reports.IncidentReportView.as_view(), name="report_incidents",),
    path("api/", include(router.urls)),
]
