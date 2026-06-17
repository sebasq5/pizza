from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import EstadoPedido, EstadoVenta, Pedido, Usuario, Venta
from app.repositories import VentaRepository
from app.services.order_service import TWO_PLACES
from app.services.audit_service import AuditService


class SaleService:
    def __init__(self, sale_repository: VentaRepository | None = None) -> None:
        self.sale_repository = sale_repository or VentaRepository()
        self.audit_service = AuditService()

    def list_sales(self) -> list[Venta]:
        return self.sale_repository.list_all()

    def get_sale_by_order_id(self, order_id: int) -> Venta | None:
        return self.sale_repository.get_by_order_id(order_id)

    def create_sale(
        self,
        order: Pedido,
        seller: Usuario,
        discount: Decimal | None = None,
    ) -> Venta:
        if self.get_sale_by_order_id(order.id) is not None:
            raise ValueError("El pedido ya tiene una venta registrada.")
        if not order.detalles:
            raise ValueError("No se puede generar una venta sin detalle.")
        if order.estado == EstadoPedido.cancelado:
            raise ValueError("No se puede generar una venta para un pedido cancelado.")

        subtotal = sum(Decimal(item.subtotal) for item in order.detalles).quantize(TWO_PLACES)
        discount_value = (discount or Decimal("0.00")).quantize(TWO_PLACES)
        if discount_value < 0:
            raise ValueError("El descuento no puede ser negativo.")
        if discount_value > subtotal:
            raise ValueError("El descuento no puede superar el subtotal.")

        impuesto = (subtotal * Decimal("0.15")).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )
        total = (subtotal + impuesto - discount_value).quantize(TWO_PLACES)

        sale = Venta(
            pedido=order,
            vendedor=seller,
            subtotal=subtotal,
            impuesto=impuesto,
            descuento=discount_value,
            total=total,
            estado=EstadoVenta.registrada,
        )
        try:
            venta = self.sale_repository.add(sale)
            self.audit_service.log_action(
                usuario_id=seller.id,
                accion="generación venta",
                tabla_afectada="ventas",
                registro_id=venta.id,
                detalle=f"Venta de ${venta.total} para pedido #{order.id}"
            )
            return venta
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo generar la venta.") from exc
    def cancel_sale(self, sale: Venta, user: Usuario) -> Venta:
        if sale.estado == EstadoVenta.anulada:
            raise ValueError("La venta ya está anulada.")
        
        estado_anterior = sale.estado
        sale.estado = EstadoVenta.anulada

        try:
            db.session.flush()

            if estado_anterior == EstadoVenta.pagada:
                from app.services.inventory_service import InventoryService
                inventory_service = InventoryService()
                inventory_service.revertir_inventario_venta(sale, user.id)

            self.audit_service.log_action(
                usuario_id=user.id,
                accion="anulación venta",
                tabla_afectada="ventas",
                registro_id=sale.id,
                detalle=f"Anulación de venta #{sale.id}"
            )

            db.session.commit()
            return sale
        except Exception as exc:
            db.session.rollback()
            raise ValueError(f"Error al anular la venta: {exc}") from exc
