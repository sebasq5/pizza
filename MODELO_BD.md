# Modelo de Base de Datos

El diseño de base de datos relacional utiliza convenciones estándar, llaves foráneas y enumeradores para mantener la integridad referencial y de dominio.

## Entidades Principales

### Usuarios y Roles
- **roles**: Define perfiles del sistema (`administrador`, `vendedor`, `cajero`, etc.).
- **usuarios**: Contiene los accesos (`usuario`, `password_hash`). FK a `roles`.

### Inventario
- **ingredientes**: Almacena materia prima (`nombre`, `unidad_medida`, `stock_actual`, `stock_minimo`).
- **productos**: Elementos vendibles finales (`nombre`, `tipo`, `precio`, `disponible`, `es_personalizable`).
- **recetas**: Tabla intermedia entre productos e ingredientes que define la composición de un producto (Bill of Materials). FK a `productos` e `ingredientes`.
- **movimientos_inventario**: Historial de ingreso o egreso manual o automático de inventario. FK a `ingredientes` y `usuarios`.

### Operaciones Core
- **clientes**: Directorio de clientes (`nombre`, `telefono`, `direccion`).
- **pedidos**: Solicitudes de los clientes (`cliente_id`, `canal`, `estado`, `total`).
- **detalles_pedido**: Productos asociados a un pedido específico (`pedido_id`, `producto_id`, `cantidad`, `subtotal`).
- **ventas**: Facturación de un pedido finalizado (`pedido_id`, `usuario_id`, `subtotal`, `descuento`, `total`, `estado`).
- **pagos**: Historial de transacciones recibidas por ventas (`venta_id`, `usuario_id`, `monto`, `metodo`, `referencia`).

### Auditoría y Control
- **cajas**: Control de sesiones de ventas para cajeros (`usuario_id`, `monto_apertura`, `monto_esperado`, `monto_real`, `diferencia`, `estado`).
- **auditoria_logs**: Tabla de logs de sistema para rastrear cambios críticos o comportamientos de los usuarios (`usuario_id`, `accion`, `entidad`, `detalles`, `fecha`).

## Restricciones y Constrains
- `ON DELETE RESTRICT`: Evita borrar registros que estén en uso (por ejemplo, no se puede borrar un producto si ya tiene ventas asociadas).
- `CHECK`: Impide inserciones de números negativos en stocks y totales.
- `Enum`: Se restringe los tipos válidos (Ej. Métodos de pago, tipos de producto, estado de pedido).
