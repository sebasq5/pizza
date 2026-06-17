from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import EstadoPedido, EstadoVenta, Pedido, Usuario, Venta
from app.repositories import VentaRepository
from app.services.order_service import TWO_PLACES


class SaleService:
    def __init__(self, sale_repository: VentaRepository | None = None) -> None:
        self.sale_repository = sale_repository or VentaRepository()

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
            return self.sale_repository.add(sale)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo generar la venta.") from exc
