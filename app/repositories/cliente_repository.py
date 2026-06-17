from sqlalchemy import select

from app.extensions import db
from app.models import Cliente


class ClienteRepository:
    def list_all(self) -> list[Cliente]:
        return list(db.session.scalars(select(Cliente).order_by(Cliente.nombre.asc())))

    def get(self, customer_id: int) -> Cliente | None:
        return db.session.get(Cliente, customer_id)

    def add(self, customer: Cliente) -> Cliente:
        db.session.add(customer)
        db.session.commit()
        return customer

    def save(self) -> None:
        db.session.commit()

    def delete(self, customer: Cliente) -> None:
        db.session.delete(customer)
        db.session.commit()
