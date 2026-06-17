from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Receta(db.Model):
    __tablename__ = "recetas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_recetas_cantidad_positive"),
        Index("ix_recetas_producto_id", "producto_id"),
        Index("ix_recetas_ingrediente_id", "ingrediente_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id", name="fk_recetas_producto_id__productos"),
        nullable=False,
    )
    ingrediente_id: Mapped[int] = mapped_column(
        ForeignKey("ingredientes.id", name="fk_recetas_ingrediente_id__ingredientes"),
        nullable=False,
    )
    cantidad: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    producto = relationship("Producto", back_populates="recetas")
    ingrediente = relationship("Ingrediente", back_populates="recetas")
