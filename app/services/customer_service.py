from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Cliente
from app.repositories import ClienteRepository


class CustomerService:
    def __init__(self, customer_repository: ClienteRepository | None = None) -> None:
        self.customer_repository = customer_repository or ClienteRepository()

    def list_customers(self) -> list[Cliente]:
        return self.customer_repository.list_all()

    def get_customer(self, customer_id: int) -> Cliente | None:
        return self.customer_repository.get(customer_id)

    def create_customer(
        self,
        name: str,
        phone: str,
        address: str | None,
        reference: str | None,
    ) -> Cliente:
        customer = Cliente(
            nombre=name.strip(),
            telefono=phone.strip(),
            direccion=address.strip() if address else None,
            referencia=reference.strip() if reference else None,
        )
        try:
            return self.customer_repository.add(customer)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo crear el cliente.") from exc

    def update_customer(
        self,
        customer: Cliente,
        name: str,
        phone: str,
        address: str | None,
        reference: str | None,
    ) -> Cliente:
        customer.nombre = name.strip()
        customer.telefono = phone.strip()
        customer.direccion = address.strip() if address else None
        customer.referencia = reference.strip() if reference else None
        try:
            self.customer_repository.save()
            return customer
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el cliente.") from exc

    def delete_customer(self, customer: Cliente) -> None:
        try:
            self.customer_repository.delete(customer)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo eliminar el cliente.") from exc
