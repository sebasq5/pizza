# Manual de Usuario

Bienvenido al sistema de Gestión de Pizzería.

## Perfiles de Usuario

- **Administrador**: Control total sobre el sistema (Catálogo, Personal, Reportes, Auditoría, Inventario).
- **Cajero**: Módulo de caja (apertura/cierre), visualización de ventas, cobro de pedidos.
- **Vendedor**: Toma de pedidos, registro de clientes.
- **Cocina / Bodeguero / Repartidor**: Tienen acceso a los apartados específicos de su función en la operación.

## Casos de Uso Comunes

### 1. Iniciar Sesión
Ingrese su nombre de usuario y contraseña brindada por su administrador. La contraseña predeterminada para demostración es `Demo123!`.

### 2. Tomar un Pedido (Vendedor)
1. Navegue a **Pedidos**.
2. Presione **Nuevo Pedido**.
3. Seleccione un Cliente (O cree uno nuevo si no existe en el sistema).
4. Especifique el canal (Mostrador, Teléfono, WhatsApp, etc.).
5. Añada los productos al pedido desde el detalle del pedido (Pizza, Bebidas).
6. Puede observar el estado del pedido a medida que avanza por cocina y entrega.

### 3. Apertura y Cobro en Caja (Cajero)
1. Antes de iniciar sus ventas, navegue a **Caja** y registre su `Apertura de Caja` indicando el fondo sencillo.
2. Vaya a **Ventas** y seleccione los pedidos pendientes por cobrar.
3. Pulse en el ícono de detalle y luego en la sección **Pagos**, registre un Nuevo Pago (Efectivo, Tarjeta, Transferencia).
4. El sistema restará automáticamente los montos. Una vez cubierta la totalidad, la venta quedará `Pagada`.

### 4. Cierre de Caja (Cajero)
1. Al finalizar su turno, diríjase a **Caja**.
2. Presione **Cerrar Caja**.
3. Ingrese el monto de efectivo (y comprobantes) que cuenta físicamente (`Monto Real`).
4. El sistema calculará la diferencia de forma automática (Cuadre de Caja).

### 5. Control de Inventario (Administrador / Bodeguero)
1. Acceda a **Inventario**.
2. Navegue por la lista de Ingredientes para verificar el `Stock Actual`. Si está en rojo, significa que el nivel se encuentra debajo del `Stock Mínimo`.
3. Vaya a `Movimientos` para registrar un ingreso (por compras) de un ingrediente específico para regularizar el inventario.

---
**Nota**: Todas sus acciones destructivas o de configuración quedarán registradas en el módulo de **Auditoría** (accesible solo para Administradores).
