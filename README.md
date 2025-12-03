# Sistema de Gestión de Reservas de Laboratorios y Préstamo de Equipos - BUAP

## 📋 Descripción del Proyecto

Sistema integral de gestión de reservas de laboratorios y préstamos de equipos desarrollado para la Benemérita Universidad Autónoma de Puebla (BUAP). Permite a estudiantes, personal técnico y administradores gestionar de manera eficiente la disponibilidad de espacios y recursos en los laboratorios de la institución.

### Objetivos Principales

- **Optimizar la utilización de espacios**: Evitar conflictos de horarios y maximizar el uso de laboratorios
- **Facilitar préstamos de equipos**: Control centralizado de inventario y prestación de equipos
- **Mejorar experiencia de usuarios**: Interfaz intuitiva y procesos simplificados
- **Generar reportes**: Estadísticas de ocupación, uso de equipos e incidentes

---

## 🎯 Funcionalidades Principales

### 1. **Gestión de Usuarios**
- Registro y autenticación mediante email y contraseña
- Tres roles de usuario: Estudiante, Técnico, Administrador
- Gestión de perfiles con matrícula única
- Sistema de autenticación basado en JWT (JSON Web Tokens)

### 2. **Gestión de Laboratorios**
- Crear y mantener registros de laboratorios
- Información de ubicación: Edificio y piso
- Control de capacidad máxima de usuarios
- Estados del laboratorio: Activo, Inactivo, Mantenimiento
- Clasificación por tipo de laboratorio

### 3. **Gestión de Equipos**
- Inventario completo de equipos por laboratorio
- Seguimiento de cantidades disponibles vs. totales
- Número de inventario para trazabilidad
- Estados de equipos: Disponible, Mantenimiento
- Descripción y documentación de equipos

### 4. **Reservas de Laboratorios**
- Crear reservas con horarios específicos
- Validación automática de conflictos de horarios
- Motivo de reserva documentado
- Estados de reserva: Pendiente, Aprobado, Rechazado, Cancelado
- Capacidad de cancelación con razón documentada
- Filtrado por laboratorio, usuario, fecha y estado

### 5. **Préstamos de Equipos**
- Solicitud de préstamo de equipos específicos
- Control de cantidades disponibles
- Registro de fecha de préstamo, devolución y entrega
- Identificación de equipos dañados durante préstamo
- Estados de préstamo: Pendiente, Aprobado, Rechazado, Devuelto, Dañado
- Notificación automática al técnico cuando se reporta equipo dañado

### 6. **Reportes y Estadísticas**
- **Reporte de Ocupación**: Tasa de ocupación por laboratorio en período especificado
- **Reporte de Uso de Equipos**: Cantidad de préstamos por equipo en rango de fechas
- **Reporte de Incidentes**: Equipos dañados reportados con detalles de fecha y estado
- Exportación de datos para análisis

---

## 📊 Matriz de Permisos por Rol

| Funcionalidad | Estudiante | Técnico | Administrador |
|---|:---:|:---:|:---:|
| **USUARIOS** |
| Ver perfil propio | ✅ | ✅ | ✅ |
| Editar perfil propio | ✅ | ✅ | ✅ |
| Listar todos usuarios | ❌ | ❌ | ✅ |
| Crear usuario | ❌ | ❌ | ✅ |
| Editar otros usuarios | ❌ | ❌ | ✅ |
| Eliminar usuario | ❌ | ❌ | ✅ |
| **LABORATORIOS** |
| Listar laboratorios | ✅ | ✅ | ✅ |
| Ver detalles laboratorio | ✅ | ✅ | ✅ |
| Crear laboratorio | ❌ | ❌ | ✅ |
| Editar laboratorio | ❌ | ❌ | ✅ |
| Eliminar laboratorio | ❌ | ❌ | ✅ |
| **EQUIPOS** |
| Listar equipos | ✅ | ✅ | ✅ |
| Ver detalles equipo | ✅ | ✅ | ✅ |
| Crear equipo | ❌ | ❌ | ✅ |
| Editar equipo | ❌ | ✅ | ✅ |
| Eliminar equipo | ❌ | ❌ | ✅ |
| **RESERVAS** |
| Crear reserva propia | ✅ | ✅ | ✅ |
| Listar propias reservas | ✅ | ✅ | ✅ |
| Listar todas reservas | ❌ | ✅ | ✅ |
| Aprobar reserva | ❌ | ✅ | ✅ |
| Rechazar reserva | ❌ | ✅ | ✅ |
| Cancelar reserva propia | ✅ | ✅ | ✅ |
| Cancelar cualquier reserva | ❌ | ✅ | ✅ |
| **PRÉSTAMOS** |
| Crear préstamo propio | ✅ | ✅ | ✅ |
| Listar propios préstamos | ✅ | ✅ | ✅ |
| Listar todos préstamos | ❌ | ✅ | ✅ |
| Aprobar préstamo | ❌ | ✅ | ✅ |
| Rechazar préstamo | ❌ | ✅ | ✅ |
| Registrar devolución | ❌ | ✅ | ✅ |
| **REPORTES** |
| Ver reportes | ❌ | ✅ | ✅ |
| Generar reporte ocupación | ❌ | ✅ | ✅ |
| Generar reporte equipos | ❌ | ✅ | ✅ |
| Generar reporte incidentes | ❌ | ✅ | ✅ |

---

## 📋 Reglas de Negocio

### Reservas
1. **Conflicto de Horarios**: No se permite crear reservas que se sobrepongan con otras aprobadas para el mismo laboratorio
2. **Aprobación Requerida**: Las reservas deben ser aprobadas por un técnico o administrador antes de considerarse válidas
3. **Cancelación**: Solo el propietario o personal autorizado puede cancelar; requiere documentar la razón
4. **Validación de Horarios**: La hora de inicio debe ser menor a la hora de fin
5. **Período de Reserva**: Máximo 12 horas de reserva continua por laboratorio por día

### Préstamos de Equipos
1. **Disponibilidad**: No se puede prestar más equipos de los disponibles en inventario
2. **Aprobación**: Todo préstamo requiere aprobación del técnico
3. **Devolución Obligatoria**: Registrar devolución es obligatorio; puede incluir daños
4. **Daño de Equipo**: Si se reporta equipo dañado, el laboratorio se notifica automáticamente
5. **Control de Inventario**: Cada préstamo aprobado decrementa inmediatamente cantidad disponible
6. **Mantenimiento**: Equipos dañados se marcan en estado "Mantenimiento" automáticamente

### Laboratorios
1. **Capacidad**: No se puede exceeder la capacidad máxima en reservas simultáneas
2. **Estado**: Solo laboratorios en estado "Activo" pueden reservarse
3. **Mantenimiento**: Se pueden crear durante mantenimiento pero aparecen como no disponibles

### Equipos
1. **Inventario Mínimo**: La cantidad disponible no puede ser menor a cero
2. **Número de Inventario**: Debe ser único y válido para trazabilidad
3. **Estado**: Equipos en "Mantenimiento" no aparecen disponibles para préstamo

---

## 🏗️ Arquitectura del Sistema

### Estructura de Capas

```
reserva_lab_api/
├── Models (Modelos de Datos)
│   ├── User (Usuario)
│   ├── Lab (Laboratorio)
│   ├── Equipment (Equipo)
│   ├── Reservation (Reserva)
│   └── Loan (Préstamo)
│
├── Serializers (Serialización)
│   ├── UserSerializer
│   ├── LabSerializer
│   ├── EquipmentSerializer
│   ├── ReservationSerializer
│   └── LoanSerializer
│
├── Views (Lógica de API)
│   ├── AuthViews (Autenticación)
│   ├── UserViewSet
│   ├── LabViewSet
│   ├── EquipmentViewSet
│   ├── ReservationViewSet
│   ├── LoanViewSet
│   └── ReportViews
│
└── Utilities (Utilidades)
    ├── Permissions (Permisos Personalizados)
    ├── Cypher Utils (Cifrado)
    └── Data Utils (Manipulación de Datos)
```

### Flujo de Datos

```
Cliente HTTP
    ↓
Django URL Router (urls.py)
    ↓
ViewSet / APIView
    ↓
Serializer (Validación)
    ↓
Models (Base de Datos)
    ↓
Response JSON
```

### Modelos de Datos

#### Usuario (User)
```python
- id (PK)
- email (única, autenticación)
- matricula (única, BUAP)
- first_name
- last_name
- role (ADMIN, TECNICO, ESTUDIANTE)
- departamento (opcional)
- carrera (opcional)
- is_active
- created_at
- updated_at
```

#### Laboratorio (Lab)
```python
- id (PK)
- nombre
- edificio
- piso
- capacidad (máximo de usuarios simultáneos)
- tipo (clasificación del lab)
- status (ACTIVO, INACTIVO, MANTENIMIENTO)
- created_at
- updated_at
```

#### Equipo (Equipo)
```python
- id (PK)
- lab (FK → Lab)
- nombre
- descripcion
- numeroInventario (único)
- cantidadTotal
- cantidadDisponible
- status (DISPONIBLE, MANTENIMIENTO)
- created_at
- updated_at
```

#### Reserva (Reservacion)
```python
- id (PK)
- user (FK → User)
- lab (FK → Lab)
- fecha
- horaInicio
- horaFin
- motivo (también se usa para cancelación)
- status (PENDIENTE, APROBADO, RECHAZADO, CANCELADO)
- created_at
- updated_at
```

#### Préstamo (Prestamo)
```python
- id (PK)
- user (FK → User)
- equipo (FK → Equipment)
- cantidad
- fechaPrestamo
- fechaDevolucion
- fechaEntrega (cuando se devuelve, nullable)
- danado (boolean, si fue dañado)
- status (PENDIENTE, APROBADO, RECHAZADO, DEVUELTO, DANADO)
- created_at
- updated_at
```

### Convención de Nombres

El proyecto utiliza **nombres en español** para mayor claridad en el dominio local:

**Campos de Base de Datos:**
- Fechas: `fecha`, `fechaInicio`, `fechaFin`, `fechaPrestamo`, `fechaEntrega`, etc.
- Horas: `horaInicio`, `horaFin`
- Cantidad: `cantidad`, `cantidadTotal`, `cantidadDisponible`
- Otros: `edificio`, `piso`, `capacidad`, `motivo`, `danado`, `razonCancelacion`

**Enumeraciones:**
- Estados: `ACTIVO`, `INACTIVO`, `MANTENIMIENTO`, `APROBADO`, `RECHAZADO`, `PENDIENTE`, `CANCELADO`, `DEVUELTO`, `DANADO`

**Variables y Métodos:**
- Se utiliza camelCase: `prestamo`, `incidentes`, `agregado`, `equipo`, `horas_reservadas`

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.12+
- MySQL 5.7+ o MariaDB
- pip

### Pasos de Instalación

#### 1. Clonar el Repositorio
```bash
git clone <url-repositorio>
cd reserva_lab_api
```

#### 2. Crear Ambiente Virtual
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/macOS
python3 -m venv env
source env/bin/activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar Base de Datos

**Crear la base de datos MySQL:**
```sql
CREATE DATABASE reserva_lab_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

**Configurar en `sistema_buap_api/settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'reserva_lab_db',
        'USER': 'root',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

#### 5. Configurar Variables de Entorno
Crear archivo `.env`:
```
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
DB_PASSWORD=tu_contraseña_mysql
JWT_SECRET=tu-jwt-secret
```

#### 6. Aplicar Migraciones
```bash
python manage.py migrate
```

#### 7. Cargar Datos de Prueba (Opcional)
```bash
python load_sample_data.py
```

#### 8. Crear Superusuario
```bash
python manage.py createsuperuser
# Email: admin@buap.mx
# Contraseña: admin123
```

#### 9. Ejecutar Servidor
```bash
python manage.py runserver
```

La API estará disponible en: **http://localhost:8000/api/**

---

## 📦 Dependencias Principales

```
Django==5.0.2                    # Framework web
djangorestframework==3.14.0      # API REST
djangorestframework-simplejwt==5.3.1  # Autenticación JWT
django-filter==24.1              # Filtrado avanzado
django-cors-headers==4.3.1       # CORS support
mysqlclient==2.2.0               # Driver MySQL
python-dotenv==1.0.0             # Variables de entorno
```

Ver `requirements.txt` para lista completa.

---

## 🔌 Endpoints principales de la API

### Autenticación
```
POST   /api/auth/login/          - Obtener tokens JWT
POST   /api/auth/refresh/        - Refrescar access token
POST   /api/auth/logout/         - Cerrar sesión
```

### Usuarios
```
GET    /api/users/               - Listar usuarios
GET    /api/users/{id}/          - Ver detalles usuario
POST   /api/users/               - Crear usuario (admin)
PATCH  /api/users/{id}/          - Editar usuario
DELETE /api/users/{id}/          - Eliminar usuario (admin)
```
Campos clave de usuario: `email`, `matricula`, `first_name`, `last_name`, `role` (ADMIN|TECNICO|ESTUDIANTE), `departamento` (opcional), `carrera` (opcional)

### Laboratorios
```
GET    /api/labs/                - Listar laboratorios
GET    /api/labs/{id}/           - Ver detalles laboratorio
POST   /api/labs/                - Crear laboratorio (admin)
PATCH  /api/labs/{id}/           - Editar laboratorio (admin)
DELETE /api/labs/{id}/           - Eliminar laboratorio (admin)
```
Modelo: `nombre`, `edificio`, `piso`, `capacidad`, `tipo`, `status`

### Equipos
```
GET    /api/equipment/           - Listar equipos
GET    /api/equipment/{id}/      - Ver detalles equipo
POST   /api/equipment/           - Crear equipo (admin)
PATCH  /api/equipment/{id}/      - Editar equipo (admin/tech)
DELETE /api/equipment/{id}/      - Eliminar equipo (admin)
```
Modelo: `nombre`, `numeroInventario`, `cantidadTotal`, `cantidadDisponible`, `status`, `lab`

### Reservas
```
GET    /api/reservations/        - Listar reservas
GET    /api/reservations/{id}/   - Ver detalles reserva
POST   /api/reservations/        - Crear reserva
PATCH  /api/reservations/{id}/   - Editar reserva propia
DELETE /api/reservations/{id}/   - Cancelar reserva
POST   /api/reservations/{id}/approve/   - Aprobar (tech/admin)
POST   /api/reservations/{id}/reject/    - Rechazar (tech/admin)
POST   /api/reservations/{id}/cancel/    - Cancelar con razón
```
Cancelación: payload `{ "motivo": "..." }` y respuesta refleja `motivo` actualizado con `status=CANCELADO`.

### Préstamos
```
GET    /api/loans/               - Listar préstamos
GET    /api/loans/{id}/          - Ver detalles préstamo
POST   /api/loans/               - Crear préstamo
POST   /api/loans/{id}/approve/  - Aprobar (tech/admin)
POST   /api/loans/{id}/reject/   - Rechazar (tech/admin)
POST   /api/loans/{id}/return/   - Registrar devolución (tech/admin)
```
Modelo: `user`, `equipo`, `cantidad`, `fechaPrestamo`, `fechaDevolucion`, `fechaEntrega`, `danado`, `status`. Usar `fechaDevolucion` en payloads y tablas (no `fechaVencimiento`).

### Reportes
```
GET    /api/reports/occupancy/   - Reporte de ocupación
GET    /api/reports/equipment-usage/ - Reporte de uso de equipos
GET    /api/reports/incidents/   - Reporte de incidentes
```

---

## 🧪 Testing

### Ejecutar Tests
```bash
python manage.py test
```

### Tests Específicos
```bash
python manage.py test sistema_buap_api.tests.TestReservations
python manage.py test sistema_buap_api.tests.TestLoans
```

---

## 🐳 Despliegue con Docker

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: reserva_lab_db
      MYSQL_ROOT_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql
  
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_NAME: reserva_lab_db
      DB_PASSWORD: password

volumes:
  mysql_data:
```

### Despliegue
```bash
docker-compose up -d
```

---

## 📈 Despliegue en Producción

### Preparación
1. Configurar `DEBUG=False` en settings.py
2. Establecer `ALLOWED_HOSTS` apropiadamente
3. Usar servidor WSGI (gunicorn, uWSGI)
4. Configurar SSL/HTTPS
5. Establecer variables de entorno seguras

### Con Gunicorn
```bash
gunicorn sistema_buap_api.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Con Nginx (Proxy)
```nginx
server {
    listen 80;
    server_name api.buap.mx;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔐 Seguridad

- **JWT**: Tokens con expiración configurable (default 8 horas)
- **CORS**: Configurado para dominios específicos
- **Permisos**: Control granular por rol en cada endpoint
- **Contraseñas**: Hashing con PBKDF2
- **Validación**: Todas las entradas validadas en serializers

### Headers de Seguridad Recomendados
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 🐛 Solución de Problemas

### Error de Conexión MySQL
```
Solución: Verificar credenciales en settings.py y estado del servidor MySQL
```

### Token JWT Inválido
```
Solución: Generar nuevo token con POST /api/auth/login/
```

### Campo no encontrado en serializer
```
Solución: Asegurar que el campo existe en models.py y está en Meta.fields
```

---

## 📝 Logging

El sistema registra actividades en:
- `logs/api.log` - Actividades generales
- `logs/errors.log` - Errores y excepciones
- Django Admin - Panel de auditoría

---

## 🤝 Contribución

1. Crear rama con nombre descriptivo: `git checkout -b feature/nueva-funcionalidad`
2. Realizar cambios y commits descriptivos
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Crear Pull Request con descripción detallada

---

## 📄 Licencia

Este proyecto está desarrollado para la BUAP. Todos los derechos reservados.

---

## 📞 Soporte

Para reportar problemas o sugerencias:
- Email: soporte@buap.mx
- Sistema de Issues: [URL del repositorio]

---

## 📚 Referencias

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
**Autor**: Equipo de Desarrollo BUAP