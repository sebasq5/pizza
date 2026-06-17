from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_pedido_cantidad_positive"),
        CheckConstraint(
            "precio_unitario >= 0",
            name="ck_detalle_pedido_precio_nonnegative",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_detalle_pedido_subtotal_nonnegative",
        ),
        Index("ix_detalle_pedido_pedido_id", "pedido_id"),
        Index("ix_detalle_pedido_producto_id", "producto_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", name="fk_detalle_pedido_pedido_id__pedidos"),
        nullable=False,
    )
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", name="fk_detalle_pedido_producto_id__productos"),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    extras: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    observaciones: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_pedido")
