from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from sistema_buap_api import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
	ordering = ("email",)
	list_display = ("email", "first_name", "last_name", "matricula", "role", "is_active")
	search_fields = ("email", "first_name", "last_name", "matricula")
	fieldsets = (
		(None, {"fields": ("email", "password", "matricula", "role")}),
		("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
		("Fechas", {"fields": ("last_login", "date_joined")}),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "password1", "password2", "matricula", "role"),
		}),
	)
	filter_horizontal = ("groups", "user_permissions")


@admin.register(models.Lab)
class LabAdmin(admin.ModelAdmin):
	list_display = ("name", "edificio", "piso", "capacidad", "status")
	list_filter = ("status",)
	search_fields = ("name", "edificio")


@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
	list_display = (
		"name",
		"numeroInventario",
		"cantidadTotal",
		"cantidadDisponible",
		"status",
	)
	list_filter = ("status",)
	search_fields = ("name", "numeroInventario")

@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
	list_display = ("id", "lab", "user", "fecha", "horaInicio", "horaFin", "status")
	list_filter = ("status", "fecha")
	search_fields = ("user__email", "lab__name")


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
	list_display = ("id", "equipo", "user", "fechaPrestamo", "fechaDevolucion", "status")
	list_filter = ("status",)
	search_fields = ("equipo__name", "user__email")