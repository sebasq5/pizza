from decimal import Decimal

import pytest

from app import create_app
from app.extensions import bcrypt, db
from app.models import (
    Cliente,
    DetallePedido,
    EstadoPedido,
    Pedido,
    Producto,
    ProductoTipo,
    Rol,
    RolNombre,
    Usuario,
    Venta,
)


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        roles = {}
        for role_name in RolNombre:
            role = Rol(nombre=role_name, descripcion=role_name.value)
            db.session.add(role)
            roles[role_name.value] = role
        db.session.flush()

        users = {
            "admin": Usuario(
                nombre="Admin",
                usuario="admin",
                password_hash=bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8"),
                rol=roles["administrador"],
                activo=True,
            ),
            "seller": Usuario(
                nombre="Seller",
                usuario="seller",
                password_hash=bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8"),
                rol=roles["vendedor"],
                activo=True,
            ),
            "kitchen": Usuario(
                nombre="Kitchen",
                usuario="kitchen",
                password_hash=bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8"),
                rol=roles["cocina"],
                activo=True,
            ),
            "delivery": Usuario(
                nombre="Delivery",
                usuario="delivery",
                password_hash=bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8"),
                rol=roles["repartidor"],
                activo=True,
            ),
        }
        for user in users.values():
            db.session.add(user)
        db.session.add(
            Producto(
                nombre="Pizza familiar",
                tipo=ProductoTipo.pizza,
                precio=Decimal("12.50"),
                disponible=True,
                es_personalizable=False,
            )
        )
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username="seller", password="ChangeMe123!"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_create_customer(client):
    login(client)
    response = client.post(
        "/admin/clientes/nuevo",
        data={
            "nombre": "Cliente Uno",
            "telefono": "0999999999",
            "direccion": "Av. Principal",
            "referencia": "Puerta azul",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        customer = db.session.query(Cliente).filter_by(nombre="Cliente Uno").one()
        assert customer.telefono == "0999999999"


def test_create_order(client):
    login(client)
    with client.application.app_context():
        customer = Cliente(
            nombre="Cliente Pedido",
            telefono="0888888888",
            direccion="Centro",
            referencia=None,
        )
        db.session.add(customer)
        db.session.commit()
        customer_id = customer.id

    response = client.post(
        "/admin/pedidos/nuevo",
        data={
            "cliente_id": customer_id,
            "canal": "presencial",
            "repartidor_id": 0,
            "direccion_entrega": "",
            "observaciones": "Sin cebolla",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        order = db.session.query(Pedido).filter_by(cliente_id=customer_id).one()
        assert order.estado == EstadoPedido.pendiente
        assert order.creador.usuario == "seller"


def test_order_detail_add_item(client):
    login(client)
    with client.application.app_context():
        customer = Cliente(nombre="Cliente Item", telefono="0777777777")
        seller = db.session.query(Usuario).filter_by(usuario="seller").one()
        product = db.session.query(Producto).filter_by(nombre="Pizza familiar").one()
        db.session.add(customer)
        db.session.flush()
        order = Pedido(
            numero="PED-TEST-1",
            cliente=customer,
            canal="presencial",
            estado="pendiente",
            telefono_contacto=customer.telefono,
            creador=seller,
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.id
        product_id = product.id

    response = client.post(
        f"/admin/pedidos/{order_id}/detalle/agregar",
        data={
            "producto_id": product_id,
            "cantidad": 2,
            "extras": "extra queso",
            "observaciones": "bien cocida",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        order = db.session.get(Pedido, order_id)
        assert len(order.detalles) == 1
        assert order.detalles[0].subtotal == Decimal("25.00")


def test_change_status(client):
    login(client, "kitchen")
    with client.application.app_context():
        customer = Cliente(nombre="Cliente Estado", telefono="0666666666")
        seller = db.session.query(Usuario).filter_by(usuario="seller").one()
        db.session.add(customer)
        db.session.flush()
        order = Pedido(
            numero="PED-TEST-2",
            cliente=customer,
            canal="presencial",
            estado=EstadoPedido.pendiente,
            telefono_contacto=customer.telefono,
            creador=seller,
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.id

    response = client.post(
        f"/admin/pedidos/{order_id}/estado",
        data={"estado": "en_cocina"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        order = db.session.get(Pedido, order_id)
        assert order.estado == EstadoPedido.en_cocina


def test_generate_sale(client):
    login(client)
    with client.application.app_context():
        customer = Cliente(nombre="Cliente Venta", telefono="0555555555")
        seller = db.session.query(Usuario).filter_by(usuario="seller").one()
        product = db.session.query(Producto).filter_by(nombre="Pizza familiar").one()
        db.session.add(customer)
        db.session.flush()
        order = Pedido(
            numero="PED-TEST-3",
            cliente=customer,
            canal="presencial",
            estado=EstadoPedido.pendiente,
            telefono_contacto=customer.telefono,
            creador=seller,
        )
        db.session.add(order)
        db.session.flush()
        db.session.add(
            DetallePedido(
                pedido=order,
                producto=product,
                cantidad=1,
                precio_unitario=Decimal("12.50"),
                subtotal=Decimal("12.50"),
            )
        )
        db.session.commit()
        order_id = order.id

    response = client.post(
        f"/admin/pedidos/{order_id}/venta",
        data={"descuento": "1.50"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        sale = db.session.query(Venta).filter_by(pedido_id=order_id).one()
        assert sale.subtotal == Decimal("12.50")
        assert sale.descuento == Decimal("1.50")
