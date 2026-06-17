from typing import Sequence

from app.extensions import db
from app.models.movimiento_inventario import MovimientoInventario


class MovimientoInventarioRepository:
    def get_all(self) -> Sequence[MovimientoInventario]:
        return db.session.scalars(
            db.select(MovimientoInventario).order_by(MovimientoInventario.fecha.desc())
        ).all()

    def create(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        db.session.add(movimiento)
        return movimiento
