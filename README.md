# Reserva Lab API

Sistema de gestión de reservas de laboratorios y préstamos de equipos para BUAP.

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip

## Instalación

1. Clonar el repositorio

2. Crear y activar un ambiente virtual:
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Crear la base de datos MySQL:
```sql
CREATE DATABASE reserva_lab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Configurar credenciales de BD en `sistema_buap_api/settings.py`

6. Aplicar migraciones:
```bash
python manage.py migrate
```

7. Crear superusuario:
```bash
python manage.py createsuperuser
```

8. Ejecutar servidor:
```bash
python manage.py runserver
```

## Arquitectura

### Modelos

- **User**: Usuario con roles (ADMIN, TECH, STUDENT)
- **Lab**: Laboratorio con estado (ACTIVE, INACTIVE, MAINTENANCE)
- **Equipment**: Equipo con inventario y disponibilidad
- **Reservation**: Reserva de laboratorio con estados y validaciones
- **Loan**: Préstamo de equipo con flujo de aprobación

### Endpoints

#### Autenticación
- `POST /api/auth/login/` - Login (JWT)
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/register/` - Registro
- `GET /api/auth/me/` - Perfil de usuario
- `PATCH /api/auth/me/` - Editar perfil

#### Usuarios (Admin only)
- `GET /api/users/` - Listar usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/:id/` - Detalle
- `PATCH /api/users/:id/` - Actualizar
- `DELETE /api/users/:id/` - Eliminar

#### Laboratorios
- `GET /api/labs/` - Listar
- `POST /api/labs/` - Crear (Admin/Tech)
- `GET /api/labs/:id/` - Detalle
- `PATCH /api/labs/:id/` - Actualizar (Admin/Tech)
- `DELETE /api/labs/:id/` - Eliminar (Admin/Tech)

Query params: `search`, `status`, `type`

#### Equipos
- `GET /api/equipment/` - Listar
- `POST /api/equipment/` - Crear (Admin/Tech)
- `GET /api/equipment/:id/` - Detalle
- `PATCH /api/equipment/:id/` - Actualizar (Admin/Tech)
- `DELETE /api/equipment/:id/` - Eliminar (Admin/Tech)

Query params: `search`, `status`, `lab`

#### Reservas
- `GET /api/reservations/` - Listar
- `POST /api/reservations/` - Crear
- `GET /api/reservations/:id/` - Detalle
- `POST /api/reservations/:id/approve/` - Aprobar (Admin/Tech)
- `POST /api/reservations/:id/reject/` - Rechazar (Admin/Tech)
- `POST /api/reservations/:id/cancel/` - Cancelar
  - Body: `{ "reason": "motivo opcional" }`

Query params: `status`, `user`, `lab`, `date`, `date_from`, `date_to`

#### Préstamos
- `GET /api/loans/` - Listar
- `POST /api/loans/` - Crear
- `GET /api/loans/:id/` - Detalle
- `POST /api/loans/:id/approve/` - Aprobar (Admin/Tech)
- `POST /api/loans/:id/reject/` - Rechazar (Admin/Tech)
- `POST /api/loans/:id/return/` - Devolver (Admin/Tech)
  - Body: `{ "damaged": boolean }`

Query params: `status`, `user`, `equipment`

#### Reportes (Admin/Tech)
- `GET /api/reports/occupancy/?period=YYYY-MM` - Tasa de ocupación de laboratorios
- `GET /api/reports/equipment-usage/?from=YYYY-MM-DD&to=YYYY-MM-DD` - Equipos más solicitados
- `GET /api/reports/incidents/?from=YYYY-MM-DD&to=YYYY-MM-DD` - Incidencias reportadas

## Reglas de Negocio

### Reservas
- No permitir reservar con fecha pasada
- Validar choques de horario para el mismo laboratorio
- Restringir reservas en laboratorios inactivos o en mantenimiento
- Cancelación requiere confirmación y (opcional) motivo

### Préstamos
- Validar disponibilidad de equipo antes de aprobar
- Registrar devoluciones y marcar daños desde el rol de Técnico/Admin
- Equipo dañado cambia a estado MAINTENANCE automáticamente

### Permisos por Rol

| Acción                    | Admin | Tech | Student |
|---------------------------|-------|------|---------|
| Ver landing page          | ✓     | ✓    | ✓       |
| Registro/Login            | ✓     | ✓    | ✓       |
| CRUD de laboratorios      | ✓     | ✗    | ✗       |
| CRUD de equipos           | ✓     | ✓    | ✗       |
| Consultar disponibilidad  | ✓     | ✓    | ✓       |
| Crear reserva             | ✓     | ✗    | ✓       |
| Aprobar/Cancelar reservas | ✓     | ✓    | ✗       |
| Crear préstamo            | ✓     | ✗    | ✓       |
| Aprobar/Cancelar préstamos| ✓     | ✓    | ✗       |
| Registrar devolución      | ✓     | ✓    | ✗       |
| Ver reportes              | ✓(globales) | ✓(su lab/equipo) | ✓(historial propio) |

## Tecnologías

- Django 5.0.2
- Django REST Framework 3.14.0
- Simple JWT 5.3.1
- MySQL
- django-filter 23.5
- django-cors-headers 4.3.1

## Despliegue

- Frontend: Vercel (Angular 19)
- Backend: Render / Google App Engine
- Base de datos: MySQL (Cloud SQL)