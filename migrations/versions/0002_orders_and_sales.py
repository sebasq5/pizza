"""orders and sales

Revision ID: 0002_orders_and_sales
Revises: 0001_initial_schema
Create Date: 2026-06-16 22:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_orders_and_sales"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


canal_pedido_enum = sa.Enum(
    "presencial",
    "whatsapp",
    "domicilio",
    name="canal_pedido_enum",
)

estado_pedido_enum = sa.Enum(
    "pendiente",
    "en_cocina",
    "listo",
    "en_reparto",
    "entregado",
    "cancelado",
    name="estado_pedido_enum",
)

estado_venta_enum = sa.Enum(
    "registrada",
    "pagada",
    "anulada",
    name="estado_venta_enum",
)


def upgrade():
    bind = op.get_bind()

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.String(length=30), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("canal", canal_pedido_enum, nullable=False),
        sa.Column("estado", estado_pedido_enum, nullable=False),
        sa.Column("direccion_entrega", sa.String(length=200), nullable=True),
        sa.Column("telefono_contacto", sa.String(length=20), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("repartidor_id", sa.Integer(), nullable=True),
        sa.Column("creado_por", sa.Integer(), nullable=False),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("btrim(numero) <> ''", name="ck_pedidos_numero_not_blank"),
        sa.CheckConstraint(
            "btrim(telefono_contacto) <> ''",
            name="ck_pedidos_telefono_contacto_not_blank",
        ),
        sa.CheckConstraint(
            "(canal <> 'domicilio') OR (direccion_entrega IS NOT NULL AND btrim(direccion_entrega) <> '')",
            name="ck_pedidos_domicilio_requiere_direccion",
        ),
        sa.CheckConstraint(
            "(repartidor_id IS NULL) OR (canal = 'domicilio')",
            name="ck_pedidos_repartidor_solo_domicilio",
        ),
        sa.CheckConstraint(
            "(estado <> 'en_reparto') OR (repartidor_id IS NOT NULL)",
            name="ck_pedidos_estado_reparto",
        ),
        sa.ForeignKeyConstraint(
            ["cliente_id"], ["clientes.id"], name="fk_pedidos_cliente_id__clientes"
        ),
        sa.ForeignKeyConstraint(
            ["creado_por"], ["usuarios.id"], name="fk_pedidos_creado_por__usuarios"
        ),
        sa.ForeignKeyConstraint(
            ["repartidor_id"],
            ["usuarios.id"],
            name="fk_pedidos_repartidor_id__usuarios",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero"),
    )
    op.create_index("ix_pedidos_cliente_id", "pedidos", ["cliente_id"], unique=False)
    op.create_index("ix_pedidos_estado", "pedidos", ["estado"], unique=False)
    op.create_index("ix_pedidos_canal", "pedidos", ["canal"], unique=False)
    op.create_index("ix_pedidos_repartidor_id", "pedidos", ["repartidor_id"], unique=False)
    op.create_index("ix_pedidos_creado_por", "pedidos", ["creado_por"], unique=False)
    op.create_index("ix_pedidos_fecha_creacion", "pedidos", ["fecha_creacion"], unique=False)

    op.create_table(
        "detalle_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("extras", sa.Text(), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint("cantidad > 0", name="ck_detalle_pedido_cantidad_positive"),
        sa.CheckConstraint(
            "precio_unitario >= 0", name="ck_detalle_pedido_precio_nonnegative"
        ),
        sa.CheckConstraint(
            "subtotal >= 0", name="ck_detalle_pedido_subtotal_nonnegative"
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"], ["pedidos.id"], name="fk_detalle_pedido_pedido_id__pedidos"
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos.id"],
            name="fk_detalle_pedido_producto_id__productos",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_detalle_pedido_pedido_id", "detalle_pedido", ["pedido_id"], unique=False
    )
    op.create_index(
        "ix_detalle_pedido_producto_id",
        "detalle_pedido",
        ["producto_id"],
        unique=False,
    )

    op.create_table(
        "ventas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("vendido_por", sa.Integer(), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("impuesto", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("descuento", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("estado", estado_venta_enum, nullable=False),
        sa.Column(
            "fecha_venta",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("subtotal >= 0", name="ck_ventas_subtotal_nonnegative"),
        sa.CheckConstraint("impuesto >= 0", name="ck_ventas_impuesto_nonnegative"),
        sa.CheckConstraint("descuento >= 0", name="ck_ventas_descuento_nonnegative"),
        sa.CheckConstraint("total >= 0", name="ck_ventas_total_nonnegative"),
        sa.CheckConstraint(
            "descuento <= subtotal", name="ck_ventas_descuento_lte_subtotal"
        ),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], name="fk_ventas_pedido_id__pedidos"),
        sa.ForeignKeyConstraint(
            ["vendido_por"],
            ["usuarios.id"],
            name="fk_ventas_vendido_por__usuarios",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pedido_id"),
    )
    op.create_index("ix_ventas_vendido_por", "ventas", ["vendido_por"], unique=False)
    op.create_index("ix_ventas_estado", "ventas", ["estado"], unique=False)
    op.create_index("ix_ventas_fecha_venta", "ventas", ["fecha_venta"], unique=False)


def downgrade():
    op.drop_index("ix_ventas_fecha_venta", table_name="ventas")
    op.drop_index("ix_ventas_estado", table_name="ventas")
    op.drop_index("ix_ventas_vendido_por", table_name="ventas")
    op.drop_table("ventas")
    op.drop_index("ix_detalle_pedido_producto_id", table_name="detalle_pedido")
    op.drop_index("ix_detalle_pedido_pedido_id", table_name="detalle_pedido")
    op.drop_table("detalle_pedido")
    op.drop_index("ix_pedidos_fecha_creacion", table_name="pedidos")
    op.drop_index("ix_pedidos_creado_por", table_name="pedidos")
    op.drop_index("ix_pedidos_repartidor_id", table_name="pedidos")
    op.drop_index("ix_pedidos_canal", table_name="pedidos")
    op.drop_index("ix_pedidos_estado", table_name="pedidos")
    op.drop_index("ix_pedidos_cliente_id", table_name="pedidos")
    op.drop_table("pedidos")
    bind = op.get_bind()
    estado_venta_enum.drop(bind, checkfirst=True)
    estado_pedido_enum.drop(bind, checkfirst=True)
    canal_pedido_enum.drop(bind, checkfirst=True)
