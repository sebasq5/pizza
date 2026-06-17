import enum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class EstadoVenta(enum.Enum):
    registrada = "registrada"
    pagada = "pagada"
    anulada = "anulada"


class Venta(db.Model):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_ventas_subtotal_nonnegative"),
        CheckConstraint("impuesto >= 0", name="ck_ventas_impuesto_nonnegative"),
        CheckConstraint("descuento >= 0", name="ck_ventas_descuento_nonnegative"),
        CheckConstraint("total >= 0", name="ck_ventas_total_nonnegative"),
        CheckConstraint(
            "descuento <= subtotal",
            name="ck_ventas_descuento_lte_subtotal",
        ),
        Index("ix_ventas_vendido_por", "vendido_por"),
        Index("ix_ventas_estado", "estado"),
        Index("ix_ventas_fecha_venta", "fecha_venta"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id", name="fk_ventas_pedido_id__pedidos"),
        nullable=False,
        unique=True,
    )
    vendido_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", name="fk_ventas_vendido_por__usuarios"),
        nullable=False,
    )
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    impuesto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    descuento: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[EstadoVenta] = mapped_column(
        Enum(EstadoVenta, name="estado_venta_enum"),
        nullable=False,
        default=EstadoVenta.registrada,
    )
    fecha_venta: Mapped[db.DateTime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    pedido = relationship("Pedido", back_populates="venta")
    vendedor = relationship("Usuario", back_populates="ventas_registradas")
