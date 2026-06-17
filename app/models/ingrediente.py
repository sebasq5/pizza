import enum

from sqlalchemy import Boolean, CheckConstraint, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class UnidadMedida(enum.Enum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"
    unidad = "unidad"


class Ingrediente(db.Model):
    __tablename__ = "ingredientes"
    __table_args__ = (
        CheckConstraint(
            "btrim(nombre) <> ''",
            name="ck_ingredientes_nombre_not_blank",
        ),
        CheckConstraint(
            "stock_actual >= 0",
            name="ck_ingredientes_stock_actual_nonnegative",
        ),
        CheckConstraint(
            "stock_minimo >= 0",
            name="ck_ingredientes_stock_minimo_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unidad_medida: Mapped[UnidadMedida] = mapped_column(
        Enum(UnidadMedida, name="unidad_medida_enum"),
        nullable=False,
    )
    stock_actual: Mapped[float] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=0,
    )
    stock_minimo: Mapped[float] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=0,
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    recetas = relationship("Receta", back_populates="ingrediente")
    movimientos = relationship("MovimientoInventario", back_populates="ingrediente")
