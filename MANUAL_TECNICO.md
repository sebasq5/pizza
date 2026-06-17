# Manual Técnico

Este documento proporciona la información necesaria para el equipo de desarrollo encargado de mantener y escalar el Sistema de Gestión de Pizzería.

## Stack Tecnológico

- **Backend**: Python 3.10+, Flask 3.x
- **Base de Datos**: SQLite (Desarrollo), PostgreSQL (Producción) vía SQLAlchemy (ORM).
- **Frontend**: HTML5, CSS3, Bootstrap 5 (vía CDN o empaquetado), Jinja2 (Templates).
- **Seguridad**: Flask-Bcrypt (Hashing), Flask-Login (Sesiones), Flask-WTF (Validación y CSRF).
- **Testing**: Pytest, Pytest-cov.
- **Despliegue**: Docker, Docker Compose, Gunicorn.

## Estructura de Directorios

```text
/pizza
├── app/
│   ├── admin/         # Controladores (Blueprints) para panel de administración.
│   ├── auth/          # Controladores para autenticación.
│   ├── main/          # Controladores públicos / dashboard principal.
│   ├── models/        # Modelos de SQLAlchemy.
│   ├── repositories/  # Clases de acceso a datos.
│   ├── services/      # Lógica de negocio (Caja, Pedidos, Auditoría).
│   ├── static/        # Archivos estáticos (CSS, JS, Imágenes).
│   └── templates/     # Plantillas Jinja2.
├── tests/             # Tests unitarios y E2E.
├── scripts/           # Scripts utilitarios.
├── migrations/        # Flask-Migrate / Alembic.
├── Dockerfile         # Receta Docker para Python.
└── docker-compose.prod.yml
```

## Patrones de Diseño Utilizados

1. **Service Repository Pattern**:
   Se implementó para separar las responsabilidades de la base de datos (Querying) y de las reglas de negocio (Logic). Evitar el acoplamiento directo entre el Request (View) y el Modelo.
2. **Dependency Injection**:
   Los servicios aceptan repositorios como parámetros en sus constructores. Permite testing unitario simulado (Mocking).
   `repo = repo or PedidoRepository()`

## Comandos Útiles

**Levantar entorno de desarrollo**:
```bash
flask run --debug
```

**Generar migraciones** (Si se alteran los modelos en `app/models/`):
```bash
flask db migrate -m "Mensaje descriptivo"
flask db upgrade
```

**Ejecutar Tests**:
```bash
pytest
pytest --cov=app tests/
```

**Poblar base de datos inicial**:
```bash
flask seed
# O usar el seeder completo
flask demo-seed
```

## Recomendaciones para Despliegue en Producción
- Utilizar `docker-compose.prod.yml` que ejecuta el servicio mediante `gunicorn` con múltiples workers en lugar del servidor local de werkzeug.
- Mantener las credenciales en un archivo `.env` seguro.
- Configurar un proxy inverso (Nginx / Traefik) con SSL (Let's Encrypt) delante del puerto 5000 para proveer encriptación HTTPS de las sesiones `SESSION_COOKIE_SECURE`.
