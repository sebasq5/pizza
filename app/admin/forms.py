from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.models import CanalPedido, EstadoPedido, ProductoTipo, RolNombre


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(), Length(min=3, max=100)],
    )
    usuario = StringField(
        "Usuario",
        validators=[DataRequired(), Length(min=3, max=50)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[Optional(), Length(min=8, max=128)],
    )
    rol = SelectField(
        "Rol",
        validators=[DataRequired()],
        choices=[(role.value, role.value.title()) for role in RolNombre],
    )
    activo = BooleanField("Activo")
    submit = SubmitField("Guardar")


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(), Length(min=2, max=100)],
    )
    tipo = SelectField(
        "Tipo",
        validators=[DataRequired()],
        choices=[(ptype.value, ptype.value.title()) for ptype in ProductoTipo],
    )
    precio = DecimalField(
        "Precio",
        validators=[DataRequired(), NumberRange(min=Decimal("0.00"))],
        places=2,
    )
    disponible = BooleanField("Disponible")
    es_personalizable = BooleanField("Personalizable")
    submit = SubmitField("Guardar")


class ClienteForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(), Length(min=2, max=100)],
    )
    telefono = StringField(
        "Telefono",
        validators=[DataRequired(), Length(min=3, max=20)],
    )
    direccion = StringField(
        "Direccion",
        validators=[Optional(), Length(max=200)],
    )
    referencia = StringField(
        "Referencia",
        validators=[Optional(), Length(max=200)],
    )
    submit = SubmitField("Guardar")


class PedidoForm(FlaskForm):
    cliente_id = SelectField("Cliente", validators=[DataRequired()], coerce=int)
    canal = SelectField(
        "Canal",
        validators=[DataRequired()],
        choices=[
            (channel.value, channel.value.replace("_", " ").title())
            for channel in CanalPedido
        ],
    )
    direccion_entrega = StringField(
        "Direccion de entrega",
        validators=[Optional(), Length(max=200)],
    )
    repartidor_id = SelectField(
        "Repartidor",
        validators=[Optional()],
        coerce=int,
        choices=[],
    )
    observaciones = TextAreaField(
        "Observaciones",
        validators=[Optional(), Length(max=1000)],
    )
    submit = SubmitField("Guardar pedido")


class DetallePedidoForm(FlaskForm):
    producto_id = SelectField("Producto", validators=[DataRequired()], coerce=int)
    cantidad = IntegerField(
        "Cantidad",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    extras = StringField("Extras", validators=[Optional(), Length(max=500)])
    observaciones = StringField(
        "Observaciones",
        validators=[Optional(), Length(max=500)],
    )
    submit = SubmitField("Agregar producto")


class ActualizarDetallePedidoForm(FlaskForm):
    cantidad = IntegerField(
        "Cantidad",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    submit = SubmitField("Actualizar")


class EstadoPedidoForm(FlaskForm):
    estado = SelectField(
        "Estado",
        validators=[DataRequired()],
        choices=[
            (status.value, status.value.replace("_", " ").title())
            for status in EstadoPedido
        ],
    )
    submit = SubmitField("Cambiar estado")


class VentaForm(FlaskForm):
    descuento = DecimalField(
        "Descuento",
        validators=[DataRequired(), NumberRange(min=Decimal("0.00"))],
        places=2,
        default=Decimal("0.00"),
    )
    submit = SubmitField("Generar venta")
