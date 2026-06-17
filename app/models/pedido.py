import enum

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class CanalPedido(enum.Enum):
    presencial = "presencial"
    whatsapp = "whatsapp"
    domicilio = "domicilio"


class EstadoPedido(enum.Enum):
    pendiente = "pendiente"
    en_cocina = "en_cocina"
    listo = "listo"
    en_reparto = "en_reparto"
    entregado = "entregado"
    cancelado = "cancelado"


class Pedido(db.Model):
    __tablename__ = "pedidos"
    __table_args__ = (
        CheckConstraint(
            "btrim(numero) <> ''",
            name="ck_pedidos_numero_not_blank",
        ),
        CheckConstraint(
            "btrim(telefono_contacto) <> ''",
            name="ck_pedidos_telefono_contacto_not_blank",
        ),
        CheckConstraint(
            "(canal <> 'domicilio') OR (direccion_entrega IS NOT NULL AND btrim(direccion_entrega) <> '')",
            name="ck_pedidos_domicilio_requiere_direccion",
        ),
        CheckConstraint(
            "(repartidor_id IS NULL) OR (canal = 'domicilio')",
            name="ck_pedidos_repartidor_solo_domicilio",
        ),
        CheckConstraint(
            "(estado <> 'en_reparto') OR (repartidor_id IS NOT NULL)",
            name="ck_pedidos_estado_reparto",
        ),
        Index("ix_pedidos_cliente_id", "cliente_id"),
        Index("ix_pedidos_estado", "estado"),
        Index("ix_pedidos_canal", "canal"),
        Index("ix_pedidos_repartidor_id", "repartidor_id"),
        Index("ix_pedidos_creado_por", "creado_por"),
        Index("ix_pedidos_fecha_creacion", "fecha_creacion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", name="fk_pedidos_cliente_id__clientes"),
        nullable=False,
    )
    canal: Mapped[CanalPedido] = mapped_column(
        Enum(CanalPedido, name="canal_pedido_enum"),
        nullable=False,
    )
    estado: Mapped[EstadoPedido] = mapped_column(
        Enum(EstadoPedido, name="estado_pedido_enum"),
        nullable=False,
        default=EstadoPedido.pendiente,
    )
    direccion_entrega: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefono_contacto: Mapped[str] = mapped_column(String(20), nullable=False)
    observaciones: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    repartidor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", name="fk_pedidos_repartidor_id__usuarios"),
        nullable=True,
    )
    creado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", name="fk_pedidos_creado_por__usuarios"),
        nullable=False,
    )
    fecha_creacion: Mapped[db.DateTime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    cliente = relationship("Cliente", back_populates="pedidos")
    creador = relationship(
        "Usuario",
        foreign_keys=[creado_por],
        back_populates="pedidos_creados",
    )
    repartidor = relationship(
        "Usuario",
        foreign_keys=[repartidor_id],
        back_populates="pedidos_repartidos",
    )
    detalles = relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )
    venta = relationship("Venta", back_populates="pedido", uselist=False)
