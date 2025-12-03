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
        TECNICO = "TECNICO", "Tecnico"
        ESTUDIANTE = "ESTUDIANTE", "Estudiante"

    username = None
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=16, choices=UserRole.choices, default=UserRole.ESTUDIANTE)
    departamento = models.CharField(max_length=255, blank=True)
    carrera = models.CharField(max_length=255, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["matricula"]

    def __str__(self):
        return f"{self.email} [{self.role}]"


class Lab(TimeStampedModel):
    class LabStatus(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"

    nombre = models.CharField(max_length=255)
    edificio = models.CharField(max_length=255)
    piso = models.CharField(max_length=32)
    capacidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=LabStatus.choices, default=LabStatus.ACTIVO)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Lab"
        verbose_name_plural = "Labs"

    def __str__(self):
        return f"{self.nombre} [{self.status}]"


class Equipo(TimeStampedModel):
    class EquipoStatus(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        MANTENIMIENTO = "MANTENIMIENTO", "Mantenimiento"

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    numeroInventario = models.CharField(max_length=64, unique=True)
    cantidadTotal = models.PositiveIntegerField()
    cantidadDisponible = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=EquipoStatus.choices, default=EquipoStatus.DISPONIBLE)
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True, related_name="equipo")

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.numeroInventario})"


class Reservacion(TimeStampedModel):
    class ReservacionStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        CANCELADO = "CANCELADO", "Cancelado"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="reservations")
    fecha = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    motivo = models.CharField(max_length=512)
    razonCancelacion = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=16, choices=ReservacionStatus.choices, default=ReservacionStatus.PENDIENTE)

    class Meta:
        ordering = ["-fecha", "-horaInicio"]

    def __str__(self):
        return f"Reservation #{self.pk}"


class Prestamo(TimeStampedModel):
    class PrestamoStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"
        DEVUELTO = "DEVUELTO", "Devuelto"
        DANADO = "DANADO", "Danado"
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="loans")
    cantidad = models.PositiveIntegerField()
    fechaPrestamo = models.DateField()
    fechaDevolucion = models.DateField()
    fechaEntrega = models.DateField(null=True, blank=True)
    danado = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=PrestamoStatus.choices, default=PrestamoStatus.PENDIENTE)

    class Meta:
        ordering = ["-fechaPrestamo"]

    def __str__(self):
        return f"Loan #{self.pk}"