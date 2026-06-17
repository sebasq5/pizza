import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ProductoTipo(enum.Enum):
    pizza = "pizza"
    lasana = "lasana"
    bebida = "bebida"
    combo = "combo"


class Producto(db.Model):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_productos_precio_nonnegative"),
        CheckConstraint("btrim(nombre) <> ''", name="ck_productos_nombre_not_blank"),
        UniqueConstraint("nombre", "tipo", name="uq_productos_nombre_tipo"),
        Index("ix_productos_tipo", "tipo"),
        Index("ix_productos_disponible", "disponible"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[ProductoTipo] = mapped_column(
        Enum(ProductoTipo, name="producto_tipo_enum"),
        nullable=False,
    )
    precio: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    es_personalizable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    detalles_pedido = relationship("DetallePedido", back_populates="producto")
