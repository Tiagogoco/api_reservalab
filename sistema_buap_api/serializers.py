from rest_framework import serializers

from sistema_buap_api import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = models.User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "matricula",
            "role",
            "password",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "matricula": {"required": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = models.User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=models.User.UserRole.choices,
        required=False,
        default=models.User.UserRole.ESTUDIANTE
    )

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "matricula": {"required": True},
        }

    def validate(self, attrs):
        # Asegurar que el rol por defecto sea STUDENT si no se especifica
        if "role" not in attrs:
            attrs["role"] = models.User.UserRole.STUDENT
        return attrs


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = UserSerializer.Meta.read_only_fields + ("role",)


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lab
        fields = (
            "id",
            "name",
            "edificio",
            "piso",
            "capacidad",
            "tipo",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = (
            "id",
            "name",
            "descripcion",
            "numeroInventario",
            "cantidadTotal",
            "cantidadDisponible",
            "status",
            "lab",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = (
            "id",
            "user",
            "lab",
            "fecha",
            "horaInicio",
            "horaFin",
            "motivo",
            "cancel_reason",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "cancel_reason", "created_at", "updated_at")

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("La hora de inicio debe ser menor que la hora de fin.")
        return super().validate(attrs)


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Loan
        fields = (
            "id",
            "user",
            "equipo",
            "cantidad",
            "fechaPrestamo",
            "fechaDevolucion",
            "fechaEntrega",
            "damaged",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value