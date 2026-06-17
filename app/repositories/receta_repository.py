from typing import Sequence

from app.extensions import db
from app.models.receta import Receta


class RecetaRepository:
    def get_by_producto_id(self, producto_id: int) -> Sequence[Receta]:
        return db.session.scalars(
            db.select(Receta).filter_by(producto_id=producto_id)
        ).all()

    def get_by_id(self, receta_id: int) -> Receta | None:
        return db.session.get(Receta, receta_id)

    def create(self, receta: Receta) -> Receta:
        db.session.add(receta)
        return receta

    def delete(self, receta: Receta) -> None:
        db.session.delete(receta)
