from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Producto, ProductoTipo
from app.repositories import ProductoRepository


from app.repositories import ProductoRepository
from app.services.audit_service import AuditService

class ProductService:
    def __init__(self, product_repository: ProductoRepository | None = None) -> None:
        self.product_repository = product_repository or ProductoRepository()
        self.audit_service = AuditService()

    def list_products(self) -> list[Producto]:
        return self.product_repository.list_all()

    def get_product(self, product_id: int) -> Producto | None:
        return self.product_repository.get(product_id)

    def create_product(
        self,
        name: str,
        product_type: str,
        price: Decimal,
        available: bool,
        customizable: bool,
    ) -> Producto:
        product = Producto(
            nombre=name.strip(),
            tipo=ProductoTipo(product_type),
            precio=price,
            disponible=available,
            es_personalizable=customizable,
        )
        try:
            product = self.product_repository.add(product)
            self.audit_service.log_action(
                accion="creación producto",
                tabla_afectada="productos",
                registro_id=product.id,
                detalle=f"Producto {product.nombre} creado a ${product.precio}"
            )
            return product
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo crear el producto.") from exc

    def update_product(
        self,
        product: Producto,
        name: str,
        product_type: str,
        price: Decimal,
        available: bool,
        customizable: bool,
    ) -> Producto:
        precio_anterior = product.precio
        product.nombre = name.strip()
        product.tipo = ProductoTipo(product_type)
        product.precio = price
        product.disponible = available
        product.es_personalizable = customizable
        try:
            self.product_repository.save()
            if precio_anterior != price:
                self.audit_service.log_action(
                    accion="cambio precio",
                    tabla_afectada="productos",
                    registro_id=product.id,
                    detalle=f"Precio cambiado de ${precio_anterior} a ${price}"
                )
            return product
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el producto.") from exc

    def delete_product(self, product: Producto) -> None:
        try:
            self.product_repository.delete(product)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo eliminar el producto.") from exc
