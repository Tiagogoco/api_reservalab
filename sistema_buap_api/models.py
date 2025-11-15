from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, matricula, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        if not matricula:
            raise ValueError("La matrícula es obligatoria")
        email = self.normalize_email(email)
        user = self.model(email=email, matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, matricula, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.UserRole.ADMIN)
        return self.create_user(email, matricula, password, **extra_fields)


class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TECH = "TECH", "Tech"
        STUDENT = "STUDENT", "Student"

    username = None
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=16, choices=UserRole.choices, default=UserRole.STUDENT)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["matricula"]

    def __str__(self):
        return f"{self.email} [{self.role}]"


class Lab(TimeStampedModel):
    class LabStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    name = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    floor = models.CharField(max_length=32)
    capacity = models.PositiveIntegerField()
    type = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=LabStatus.choices, default=LabStatus.ACTIVE)

    class Meta:
        ordering = ["name"]
        verbose_name = "Lab"
        verbose_name_plural = "Labs"

    def __str__(self):
        return f"{self.name} [{self.status}]"


class Equipment(TimeStampedModel):
    class EquipmentStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    inventory_number = models.CharField(max_length=64, unique=True)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=EquipmentStatus.choices, default=EquipmentStatus.AVAILABLE)
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True, related_name="equipment")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"


class Reservation(TimeStampedModel):
    class ReservationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="reservations")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=512)
    cancel_reason = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=16, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"Reservation #{self.pk}"


class Loan(TimeStampedModel):
    class LoanStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RETURNED = "RETURNED", "Returned"
        DAMAGED = "DAMAGED", "Damaged"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="loans")
    quantity = models.PositiveIntegerField()
    loan_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    damaged = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=LoanStatus.choices, default=LoanStatus.PENDING)

    class Meta:
        ordering = ["-loan_date"]

    def __str__(self):
        return f"Loan #{self.pk}"