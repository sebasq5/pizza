# Sistema de Gestión de Pizzería

Un sistema completo de gestión de punto de venta (POS) y administración para una Pizzería, construido con Flask, SQLAlchemy y tecnologías modernas. 

## Características Principales

*   **Autenticación y Autorización**: Sistema basado en roles (Administrador, Vendedor, Cajero, Cocina, Bodeguero, Repartidor).
*   **Gestión de Inventario**: Control de ingredientes, stock mínimo y actualizaciones automáticas.
*   **Ventas y Pedidos**: Flujo completo desde la toma del pedido hasta la facturación y pago.
*   **Control de Caja**: Apertura, cierre y cuadre de caja con reportes de diferencias.
*   **Auditoría**: Trazabilidad completa de las acciones de los usuarios en el sistema.
*   **Arquitectura Robusta**: Patrón Service/Repository, inyección de dependencias y validaciones estrictas.
*   **Seguridad Integral**: Hashing seguro, protección CSRF y prevención de inyección SQL.

## 🚀 Guía Completa de Instalación

El sistema puede ser instalado de dos maneras: usando Docker (Recomendado para producción y pruebas rápidas) o de manera local.

### Opción A: Instalación con Docker (Recomendado)

1. **Clonar el repositorio y entrar al directorio:**
   ```bash
   git clone https://github.com/sebasq5/pizza.git
   cd pizza
   ```
2. **Configurar Entorno:**  
   Copia el archivo de ejemplo a un archivo oculto `.env` (o renómbralo):
   ```bash
   cp .env.example .env
   ```
   *(Opcional: puedes editar las credenciales dentro de `.env` a tu gusto).*

3. **Ejecutar el Entorno Docker:**  
   Esto descargará la imagen de la base de datos (PostgreSQL), construirá la aplicación e iniciará todo.
   ```bash
   docker compose up --build -d
   ```

4. **Poblar la base de datos con datos de prueba (Opcional):**
   ```bash
   docker compose exec web flask demo-seed
   ```

5. **Acceso:**  
   Ingresa a `http://localhost:5000` con el usuario `admin` y contraseña `Demo123!`.

---

### Opción B: Instalación Local (Para Desarrolladores)

1. **Crear un Entorno Virtual y Activarlo:**
   ```bash
   python -m venv .venv
   # En Windows:
   .\.venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

2. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar Base de Datos Local:**  
   Asegúrate de tener un servidor PostgreSQL ejecutándose y actualiza la variable `DATABASE_URL` en tu archivo `.env`. Alternativamente, para desarrollo rápido sin PostgreSQL, puedes cambiar la cadena de conexión en `.env` a SQLite: `DATABASE_URL=sqlite:///pizza.db`

4. **Inicializar y Migrar la Base de Datos:**
   ```bash
   flask db upgrade
   flask demo-seed
   ```

5. **Ejecutar el Servidor:**
   ```bash
   flask run
   ```

## Documentación de Seguridad

- **`INFORME_PENTESTING.md`**: Evaluación detallada de seguridad de la aplicación con recomendaciones aplicadas.
