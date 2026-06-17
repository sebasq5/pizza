from app.extensions import db
from app.models import DetallePedido


class DetallePedidoRepository:
    def get(self, item_id: int) -> DetallePedido | None:
        return db.session.get(DetallePedido, item_id)

    def add(self, item: DetallePedido) -> DetallePedido:
        db.session.add(item)
        db.session.commit()
        return item

    def save(self) -> None:
        db.session.commit()

    def delete(self, item: DetallePedido) -> None:
        db.session.delete(item)
        db.session.commit()
