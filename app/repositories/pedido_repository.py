from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import DetallePedido, Pedido


class PedidoRepository:
    def _base_query(self):
        return select(Pedido).options(
            selectinload(Pedido.cliente),
            selectinload(Pedido.repartidor),
            selectinload(Pedido.creador),
            selectinload(Pedido.detalles).selectinload(DetallePedido.producto),
            selectinload(Pedido.venta),
        )

    def list_all(self) -> list[Pedido]:
        query = self._base_query().order_by(Pedido.fecha_creacion.desc())
        return list(db.session.scalars(query).unique())

    def list_by_repartidor(self, user_id: int) -> list[Pedido]:
        query = (
            self._base_query()
            .where(Pedido.repartidor_id == user_id)
            .order_by(Pedido.fecha_creacion.desc())
        )
        return list(db.session.scalars(query).unique())

    def get(self, order_id: int) -> Pedido | None:
        return db.session.scalar(self._base_query().where(Pedido.id == order_id))

    def add(self, order: Pedido) -> Pedido:
        db.session.add(order)
        db.session.commit()
        return order

    def save(self) -> None:
        db.session.commit()
