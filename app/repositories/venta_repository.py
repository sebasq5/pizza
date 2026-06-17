from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Pedido, Venta


class VentaRepository:
    def list_all(self) -> list[Venta]:
        query = (
            select(Venta)
            .options(
                selectinload(Venta.pedido).selectinload(Pedido.cliente),
                selectinload(Venta.vendedor),
            )
            .order_by(Venta.fecha_venta.desc())
        )
        return list(db.session.scalars(query).unique())

    def get_by_order_id(self, order_id: int) -> Venta | None:
        return db.session.scalar(select(Venta).where(Venta.pedido_id == order_id))

    def get_by_id(self, venta_id: int) -> Venta | None:
        return db.session.get(Venta, venta_id)

    def add(self, sale: Venta) -> Venta:
        db.session.add(sale)
        db.session.commit()
        return sale
