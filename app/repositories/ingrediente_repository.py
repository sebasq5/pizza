from typing import Sequence

from app.extensions import db
from app.models.ingrediente import Ingrediente


class IngredienteRepository:
    def get_all(self) -> Sequence[Ingrediente]:
        return db.session.scalars(db.select(Ingrediente).order_by(Ingrediente.nombre)).all()

    def get_by_id(self, ingrediente_id: int) -> Ingrediente | None:
        return db.session.get(Ingrediente, ingrediente_id)

    def create(self, ingrediente: Ingrediente) -> Ingrediente:
        db.session.add(ingrediente)
        return ingrediente
