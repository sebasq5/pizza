import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class RolNombre(enum.Enum):
    administrador = "administrador"
    vendedor = "vendedor"
    cajero = "cajero"
    cocina = "cocina"
    bodeguero = "bodeguero"
    repartidor = "repartidor"


class Rol(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[RolNombre] = mapped_column(
        Enum(RolNombre, name="rol_nombre_enum"),
        unique=True,
        nullable=False,
    )
    descripcion: Mapped[str | None] = mapped_column(String(150), nullable=True)

    usuarios = relationship("Usuario", back_populates="rol")
