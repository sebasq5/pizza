"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-16 20:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


rol_nombre_enum = sa.Enum(
    "administrador",
    "vendedor",
    "cajero",
    "cocina",
    "bodeguero",
    "repartidor",
    name="rol_nombre_enum",
)

producto_tipo_enum = sa.Enum(
    "pizza",
    "lasana",
    "bebida",
    "combo",
    name="producto_tipo_enum",
)


def upgrade():
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=False),
        sa.Column("direccion", sa.String(length=200), nullable=True),
        sa.Column("referencia", sa.String(length=200), nullable=True),
        sa.CheckConstraint("btrim(nombre) <> ''", name="ck_clientes_nombre_not_blank"),
        sa.CheckConstraint(
            "btrim(telefono) <> ''",
            name="ck_clientes_telefono_not_blank",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clientes_nombre", "clientes", ["nombre"], unique=False)
    op.create_index("ix_clientes_telefono", "clientes", ["telefono"], unique=False)

    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("tipo", producto_tipo_enum, nullable=False),
        sa.Column("precio", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("disponible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "es_personalizable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.CheckConstraint("precio >= 0", name="ck_productos_precio_nonnegative"),
        sa.CheckConstraint("btrim(nombre) <> ''", name="ck_productos_nombre_not_blank"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", "tipo", name="uq_productos_nombre_tipo"),
    )
    op.create_index("ix_productos_disponible", "productos", ["disponible"], unique=False)
    op.create_index("ix_productos_tipo", "productos", ["tipo"], unique=False)

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", rol_nombre_enum, nullable=False),
        sa.Column("descripcion", sa.String(length=150), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("usuario", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("btrim(nombre) <> ''", name="ck_usuarios_nombre_not_blank"),
        sa.CheckConstraint("btrim(usuario) <> ''", name="ck_usuarios_usuario_not_blank"),
        sa.ForeignKeyConstraint(
            ["rol_id"],
            ["roles.id"],
            name="fk_usuarios_rol_id__roles",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario"),
    )
    op.create_index("ix_usuarios_activo", "usuarios", ["activo"], unique=False)
    op.create_index("ix_usuarios_rol_id", "usuarios", ["rol_id"], unique=False)


def downgrade():
    op.drop_index("ix_usuarios_rol_id", table_name="usuarios")
    op.drop_index("ix_usuarios_activo", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("roles")
    op.drop_index("ix_productos_tipo", table_name="productos")
    op.drop_index("ix_productos_disponible", table_name="productos")
    op.drop_table("productos")
    op.drop_index("ix_clientes_telefono", table_name="clientes")
    op.drop_index("ix_clientes_nombre", table_name="clientes")
    op.drop_table("clientes")
    producto_tipo_enum.drop(op.get_bind(), checkfirst=False)
    rol_nombre_enum.drop(op.get_bind(), checkfirst=False)
