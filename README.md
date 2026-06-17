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

## Requisitos Previos

*   Docker y Docker Compose (Recomendado para producción)
*   Python 3.10+ (Para entorno local sin Docker)

## Instalación rápida (Docker)

1. Clonar el repositorio.
2. Copiar `.env.example` a `.env` y ajustar las variables necesarias.
3. Ejecutar el entorno:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
4. Poblar datos de demostración:
   ```bash
   docker compose -f docker-compose.prod.yml exec web flask demo-seed
   ```
5. Acceder a `http://localhost:5000` con el usuario `admin` y contraseña `Demo123!`.

## Documentación

Para más información, consulte la documentación adicional en el directorio raíz:
- `ARQUITECTURA.md`
- `MODELO_BD.md`
- `MANUAL_USUARIO.md`
- `MANUAL_TECNICO.md`
- `PENTEST_REPORT.md`
