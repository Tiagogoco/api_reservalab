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
	list_display = ("name", "building", "floor", "capacity", "status")
	list_filter = ("status",)
	search_fields = ("name", "building")


@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
	list_display = (
		"name",
		"inventory_number",
		"total_quantity",
		"available_quantity",
		"status",
	)
	list_filter = ("status",)
	search_fields = ("name", "inventory_number")


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
	list_display = ("id", "lab", "user", "date", "start_time", "end_time", "status")
	list_filter = ("status", "date")
	search_fields = ("user__email", "lab__name")


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
	list_display = ("id", "equipment", "user", "loan_date", "due_date", "status")
	list_filter = ("status",)
	search_fields = ("equipment__name", "user__email")
