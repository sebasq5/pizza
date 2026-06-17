import enum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class MetodoPago(enum.Enum):
    efectivo = "efectivo"
    transferencia = "transferencia"
    tarjeta = "tarjeta"


class Pago(db.Model):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_pagos_monto_positive"),
        CheckConstraint(
            "(metodo = 'efectivo') OR (btrim(referencia) <> '')",
            name="ck_pagos_referencia_requerida_tarjeta_transferencia",
        ),
        Index("ix_pagos_venta_id", "venta_id"),
        Index("ix_pagos_responsable_id", "responsable_id"),
        Index("ix_pagos_fecha", "fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    venta_id: Mapped[int] = mapped_column(
        ForeignKey("ventas.id", name="fk_pagos_venta_id__ventas"),
        nullable=False,
    )
    metodo: Mapped[MetodoPago] = mapped_column(
        Enum(MetodoPago, name="metodo_pago_enum"),
        nullable=False,
    )
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsable_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", name="fk_pagos_responsable_id__usuarios"),
        nullable=False,
    )
    fecha: Mapped[db.DateTime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    venta = relationship("Venta", back_populates="pagos")
    responsable = relationship("Usuario", back_populates="pagos_registrados")
