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
        # Enforce role-based fields
        role = validated_data.get("role", models.User.UserRole.ESTUDIANTE)
        if role == models.User.UserRole.ESTUDIANTE:
            # estudiante: carrera permitido; departamento inválido
            validated_data["departamento"] = ""
        else:
            # tecnico/admin: departamento permitido; carrera inválido
            validated_data["carrera"] = ""
        user = models.User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        # Enforce role-based fields on update
        role = validated_data.get("role", instance.role)
        if role == models.User.UserRole.ESTUDIANTE:
            validated_data["departamento"] = ""
        else:
            validated_data["carrera"] = ""
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
        # Rol por defecto: ESTUDIANTE
        role = attrs.get("role", models.User.UserRole.ESTUDIANTE)
        attrs["role"] = role
        # Regla de negocio: carrera solo para ESTUDIANTE; departamento solo para TECNICO/ADMIN
        if role == models.User.UserRole.ESTUDIANTE:
            # limpiar departamento si viene
            if "departamento" in attrs:
                attrs["departamento"] = ""
        else:
            # limpiar carrera si viene
            if "carrera" in attrs:
                attrs["carrera"] = ""
        return attrs


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = UserSerializer.Meta.read_only_fields + ("role",)


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lab
        fields = (
            "id",
            "nombre",
            "edificio",
            "piso",
            "capacidad",
            "tipo",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipo
        fields = (
            "id",
            "nombre",
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


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservacion
        fields = (
            "id",
            "user",
            "lab",
            "fecha",
            "horaInicio",
            "horaFin",
            "motivo",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        horaInicio = attrs.get("horaInicio")
        horaFin = attrs.get("horaFin")
        if horaInicio and horaFin and horaInicio >= horaFin:
            raise serializers.ValidationError("La hora de inicio debe ser menor que la hora de fin.")
        return super().validate(attrs)


class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prestamo
        fields = (
            "id",
            "user",
            "equipo",
            "cantidad",
            "fechaPrestamo",
            "fechaDevolucion",
            "fechaEntrega",
            "danado",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value