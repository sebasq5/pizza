from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Producto, ProductoTipo
from app.repositories import ProductoRepository


class ProductService:
    def __init__(self, product_repository: ProductoRepository | None = None) -> None:
        self.product_repository = product_repository or ProductoRepository()

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
            return self.product_repository.add(product)
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
        product.nombre = name.strip()
        product.tipo = ProductoTipo(product_type)
        product.precio = price
        product.disponible = available
        product.es_personalizable = customizable
        try:
            self.product_repository.save()
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
