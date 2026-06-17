from sqlalchemy import select

from app.extensions import db
from app.models import Producto


class ProductoRepository:
    def list_all(self) -> list[Producto]:
        return list(db.session.scalars(select(Producto).order_by(Producto.nombre.asc())))

    def get(self, product_id: int) -> Producto | None:
        return db.session.get(Producto, product_id)

    def add(self, product: Producto) -> Producto:
        db.session.add(product)
        db.session.commit()
        return product

    def save(self) -> None:
        db.session.commit()

    def delete(self, product: Producto) -> None:
        db.session.delete(product)
        db.session.commit()
