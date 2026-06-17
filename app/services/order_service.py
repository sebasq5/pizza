from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import (
    CanalPedido,
    DetallePedido,
    EstadoPedido,
    Pedido,
    RolNombre,
    Usuario,
)
from app.repositories import (
    ClienteRepository,
    DetallePedidoRepository,
    PedidoRepository,
    ProductoRepository,
    UsuarioRepository,
)


TWO_PLACES = Decimal("0.01")


class OrderService:
    def __init__(
        self,
        order_repository: PedidoRepository | None = None,
        customer_repository: ClienteRepository | None = None,
        product_repository: ProductoRepository | None = None,
        item_repository: DetallePedidoRepository | None = None,
        user_repository: UsuarioRepository | None = None,
    ) -> None:
        self.order_repository = order_repository or PedidoRepository()
        self.customer_repository = customer_repository or ClienteRepository()
        self.product_repository = product_repository or ProductoRepository()
        self.item_repository = item_repository or DetallePedidoRepository()
        self.user_repository = user_repository or UsuarioRepository()

    def list_orders_for_user(self, user: Usuario) -> list[Pedido]:
        if user.role_name == RolNombre.repartidor.value:
            return self.order_repository.list_by_repartidor(user.id)
        return self.order_repository.list_all()

    def list_delivery_users(self) -> list[Usuario]:
        return self.user_repository.list_active_by_role(RolNombre.repartidor)

    def get_order(self, order_id: int) -> Pedido | None:
        return self.order_repository.get(order_id)

    def get_order_or_raise_access(self, order_id: int, user: Usuario) -> Pedido:
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("Pedido no encontrado.")
        if user.role_name == RolNombre.repartidor.value and order.repartidor_id != user.id:
            raise PermissionError("No tienes acceso a este pedido.")
        return order

    def create_order(
        self,
        customer_id: int,
        channel: str,
        creator: Usuario,
        address: str | None,
        notes: str | None,
        delivery_user_id: int | None = None,
    ) -> Pedido:
        customer = self.customer_repository.get(customer_id)
        if customer is None:
            raise ValueError("Cliente invalido.")

        canal = CanalPedido(channel)
        address_value = address.strip() if address else None
        if canal == CanalPedido.domicilio and not address_value:
            raise ValueError("La direccion es obligatoria para pedidos a domicilio.")

        delivery_user = None
        if delivery_user_id:
            delivery_user = self.user_repository.get(delivery_user_id)
            if delivery_user is None or delivery_user.role_name != RolNombre.repartidor.value:
                raise ValueError("Repartidor invalido.")
            if canal != CanalPedido.domicilio:
                raise ValueError("Solo los pedidos a domicilio pueden asignar repartidor.")

        order = Pedido(
            numero=self._generate_order_number(),
            cliente=customer,
            canal=canal,
            estado=EstadoPedido.pendiente,
            direccion_entrega=address_value,
            telefono_contacto=customer.telefono,
            observaciones=notes.strip() if notes else None,
            repartidor=delivery_user,
            creador=creator,
        )
        try:
            return self.order_repository.add(order)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo crear el pedido.") from exc

    def update_order(
        self,
        order: Pedido,
        customer_id: int,
        channel: str,
        address: str | None,
        notes: str | None,
        delivery_user_id: int | None,
    ) -> Pedido:
        self._ensure_order_editable(order)
        customer = self.customer_repository.get(customer_id)
        if customer is None:
            raise ValueError("Cliente invalido.")

        canal = CanalPedido(channel)
        address_value = address.strip() if address else None
        if canal == CanalPedido.domicilio and not address_value:
            raise ValueError("La direccion es obligatoria para pedidos a domicilio.")

        delivery_user = None
        if delivery_user_id:
            delivery_user = self.user_repository.get(delivery_user_id)
            if delivery_user is None or delivery_user.role_name != RolNombre.repartidor.value:
                raise ValueError("Repartidor invalido.")
            if canal != CanalPedido.domicilio:
                raise ValueError("Solo los pedidos a domicilio pueden asignar repartidor.")

        order.cliente = customer
        order.canal = canal
        order.direccion_entrega = address_value
        order.telefono_contacto = customer.telefono
        order.observaciones = notes.strip() if notes else None
        order.repartidor = delivery_user
        try:
            self.order_repository.save()
            return order
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el pedido.") from exc

    def add_order_item(
        self,
        order: Pedido,
        product_id: int,
        quantity: int,
        extras: str | None = None,
        notes: str | None = None,
    ) -> DetallePedido:
        self._ensure_order_editable(order)
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        product = self.product_repository.get(product_id)
        if product is None or not product.disponible:
            raise ValueError("Producto invalido o no disponible.")

        subtotal = (Decimal(product.precio) * Decimal(quantity)).quantize(TWO_PLACES)
        item = DetallePedido(
            pedido=order,
            producto=product,
            cantidad=quantity,
            precio_unitario=product.precio,
            extras=extras.strip() if extras else None,
            observaciones=notes.strip() if notes else None,
            subtotal=subtotal,
        )
        try:
            return self.item_repository.add(item)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo agregar el producto al pedido.") from exc

    def update_order_item(self, item: DetallePedido, quantity: int) -> DetallePedido:
        self._ensure_order_editable(item.pedido)
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        item.cantidad = quantity
        item.subtotal = (
            Decimal(item.precio_unitario) * Decimal(quantity)
        ).quantize(TWO_PLACES)
        try:
            self.item_repository.save()
            return item
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el detalle.") from exc

    def remove_order_item(self, item: DetallePedido) -> None:
        self._ensure_order_editable(item.pedido)
        try:
            self.item_repository.delete(item)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo eliminar el detalle.") from exc

    def change_status(self, order: Pedido, new_status: str, actor: Usuario) -> Pedido:
        target_status = EstadoPedido(new_status)
        self._authorize_status_change(order, target_status, actor)
        self._validate_status_transition(order.estado, target_status, order)
        order.estado = target_status
        try:
            self.order_repository.save()
            return order
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el estado.") from exc

    def order_subtotal(self, order: Pedido) -> Decimal:
        total = sum(Decimal(item.subtotal) for item in order.detalles)
        return Decimal(total).quantize(TWO_PLACES)

    def available_products(self):
        return [product for product in self.product_repository.list_all() if product.disponible]

    def get_item(self, item_id: int) -> DetallePedido | None:
        return self.item_repository.get(item_id)

    def _generate_order_number(self) -> str:
        last_id = db.session.scalar(select(func.max(Pedido.id))) or 0
        return f"PED-{last_id + 1:06d}"

    def _ensure_order_editable(self, order: Pedido) -> None:
        if order.venta is not None:
            raise ValueError("No puedes modificar un pedido que ya tiene venta.")
        if order.estado != EstadoPedido.pendiente:
            raise ValueError("Solo los pedidos pendientes pueden modificarse.")

    def _authorize_status_change(
        self,
        order: Pedido,
        target_status: EstadoPedido,
        actor: Usuario,
    ) -> None:
        role_name = actor.role_name
        if role_name == RolNombre.administrador.value:
            return
        if role_name == RolNombre.cocina.value:
            if target_status not in {EstadoPedido.en_cocina, EstadoPedido.listo}:
                raise PermissionError("Cocina solo puede actualizar estados operativos.")
            return
        if role_name == RolNombre.repartidor.value:
            if order.repartidor_id != actor.id:
                raise PermissionError("Solo puedes gestionar pedidos asignados.")
            if target_status not in {EstadoPedido.en_reparto, EstadoPedido.entregado}:
                raise PermissionError("Repartidor solo puede gestionar entrega.")
            return
        if role_name == RolNombre.vendedor.value:
            if target_status not in {EstadoPedido.cancelado, EstadoPedido.pendiente}:
                raise PermissionError("Vendedor no puede usar ese cambio de estado.")
            return
        raise PermissionError("No tienes permisos para cambiar el estado.")

    def _validate_status_transition(
        self,
        current_status: EstadoPedido,
        target_status: EstadoPedido,
        order: Pedido,
    ) -> None:
        allowed = {
            EstadoPedido.pendiente: {EstadoPedido.en_cocina, EstadoPedido.cancelado},
            EstadoPedido.en_cocina: {EstadoPedido.listo, EstadoPedido.cancelado},
            EstadoPedido.listo: {
                EstadoPedido.en_reparto,
                EstadoPedido.entregado,
                EstadoPedido.cancelado,
            },
            EstadoPedido.en_reparto: {EstadoPedido.entregado, EstadoPedido.cancelado},
            EstadoPedido.entregado: set(),
            EstadoPedido.cancelado: set(),
        }
        if target_status == current_status:
            return
        if target_status not in allowed[current_status]:
            raise ValueError("Transicion de estado no permitida.")
        if target_status == EstadoPedido.en_reparto and order.repartidor_id is None:
            raise ValueError("Debes asignar un repartidor antes de enviar a reparto.")
