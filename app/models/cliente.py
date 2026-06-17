from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"
    __table_args__ = (
        CheckConstraint("btrim(nombre) <> ''", name="ck_clientes_nombre_not_blank"),
        CheckConstraint(
            "btrim(telefono) <> ''",
            name="ck_clientes_telefono_not_blank",
        ),
        Index("ix_clientes_nombre", "nombre"),
        Index("ix_clientes_telefono", "telefono"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    referencia: Mapped[str | None] = mapped_column(String(200), nullable=True)

    pedidos = relationship("Pedido", back_populates="cliente")
