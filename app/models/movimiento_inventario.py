import enum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class TipoMovimiento(enum.Enum):
    entrada = "entrada"
    salida = "salida"
    ajuste = "ajuste"


class MotivoMovimiento(enum.Enum):
    compra = "compra"
    venta = "venta"
    merma = "merma"
    consumo_interno = "consumo_interno"
    cancelacion = "cancelacion"
    ajuste_manual = "ajuste_manual"


class MovimientoInventario(db.Model):
    __tablename__ = "movimientos_inventario"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_movimientos_cantidad_positive"),
        Index("ix_movimientos_ingrediente_id", "ingrediente_id"),
        Index("ix_movimientos_responsable_id", "responsable_id"),
        Index("ix_movimientos_fecha", "fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey(
            "ingredientes.id",
            name="fk_movimientos_ingrediente_id__ingredientes",
        ),
        nullable=False,
    )
    tipo: Mapped[TipoMovimiento] = mapped_column(
        Enum(TipoMovimiento, name="tipo_movimiento_enum"),
        nullable=False,
    )
    motivo: Mapped[MotivoMovimiento] = mapped_column(
        Enum(MotivoMovimiento, name="motivo_movimiento_enum"),
        nullable=False,
    )
    cantidad: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    responsable_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", name="fk_movimientos_responsable_id__usuarios"),
        nullable=False,
    )
    fecha: Mapped[db.DateTime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    ingrediente = relationship("Ingrediente", back_populates="movimientos")
    responsable = relationship("Usuario", back_populates="movimientos_inventario")
