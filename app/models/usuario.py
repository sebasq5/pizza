from flask_login import UserMixin
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("btrim(nombre) <> ''", name="ck_usuarios_nombre_not_blank"),
        CheckConstraint(
            "btrim(usuario) <> ''",
            name="ck_usuarios_usuario_not_blank",
        ),
        Index("ix_usuarios_rol_id", "rol_id"),
        Index("ix_usuarios_activo", "activo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", name="fk_usuarios_rol_id__roles"),
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_creacion: Mapped[db.DateTime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    rol = relationship("Rol", back_populates="usuarios")
    pedidos_creados = relationship(
        "Pedido",
        foreign_keys="Pedido.creado_por",
        back_populates="creador",
    )
    pedidos_repartidos = relationship(
        "Pedido",
        foreign_keys="Pedido.repartidor_id",
        back_populates="repartidor",
    )
    ventas_registradas = relationship("Venta", back_populates="vendedor")
    pagos_registrados = relationship("Pago", back_populates="responsable")
    movimientos_inventario = relationship("MovimientoInventario", back_populates="responsable")
    def get_id(self) -> str:
        return str(self.id)

    @property
    def role_name(self) -> str:
        return self.rol.nombre.value
