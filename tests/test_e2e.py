import pytest
from flask import url_for
from app.models import Usuario, RolNombre, Producto, Cliente, Pedido, Venta, Caja, EstadoPedido, EstadoCaja
from decimal import Decimal
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Compatibilidad con btrim de Postgres en SQLite para tests E2E
class btrim(FunctionElement):
    name = 'btrim'
    inherit_cache = True

@compiles(btrim, 'sqlite')
def compile_btrim_sqlite(element, compiler, **kw):
    return "trim(%s)" % compiler.process(element.clauses, **kw)

@event.listens_for(Engine, "connect")
def sqlite_engine_connect(dbapi_connection, connection_record):
    if type(dbapi_connection).__name__ == "Connection":
        try:
            dbapi_connection.create_function("btrim", 1, lambda x: x.strip() if x else x)
        except AttributeError:
            pass

from app import create_app
from app.extensions import bcrypt, db
from app.models import Rol

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

        test_user = Usuario(
            nombre="Admin E2E",
            usuario="admine2e",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            rol=roles["administrador"],
            activo=True,
        )
        db.session.add(test_user)

        test_cajero = Usuario(
            nombre="Cajero E2E",
            usuario="cajeroe2e",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            rol=roles["cajero"],
            activo=True,
        )
        db.session.add(test_cajero)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def db_session(app):
    return db.session

def test_flujo_completo_e2e(client, db_session):
    # 1. AUTENTICACIÓN
    response = client.post("/login", data={"username": "admine2e", "password": "password123"}, follow_redirects=True)
    assert response.status_code == 200

    # 2. CAJA - Apertura
    response = client.post("/admin/caja/abrir", data={"monto_apertura": "50.00"}, follow_redirects=True)
    assert response.status_code == 200
    caja = db_session.query(Caja).filter_by(estado=EstadoCaja.abierta).first()
    assert caja is not None

    # 3. CREACIÓN DE CLIENTE Y PRODUCTO (Preparación para pedidos)
    cliente = Cliente(nombre="Cliente E2E", telefono="0999999999", direccion="Test Dir", referencia="Test Ref")
    db_session.add(cliente)
    producto = Producto(nombre="Pizza E2E", tipo="pizza", precio=Decimal("12.50"), disponible=True, es_personalizable=False)
    db_session.add(producto)
    db_session.commit()

    # 4. PEDIDOS
    response = client.post("/admin/pedidos/create", data={
        "cliente_id": cliente.id, "canal": "mostrador", "observaciones": ""
    }, follow_redirects=True)
    assert response.status_code == 200
    pedido = db_session.query(Pedido).first()
    assert pedido is not None

    # Agregar detalle al pedido
    client.post(f"/admin/pedidos/{pedido.id}/add", data={
        "producto_id": producto.id, "cantidad": 2, "extras": "", "observaciones": ""
    }, follow_redirects=True)
    db_session.refresh(pedido)
    
    # 5. VENTAS
    response = client.post(f"/admin/pedidos/{pedido.id}/venta", data={
        "descuento": "5.00"
    }, follow_redirects=True)
    assert response.status_code == 200
    venta = db_session.query(Venta).filter_by(pedido_id=pedido.id).first()
    assert venta is not None

    # 6. PAGOS
    response = client.post(f"/admin/ventas/{venta.id}/pagos", data={
        "metodo": "efectivo", "monto": "20.00", "referencia": ""
    }, follow_redirects=True)
    assert response.status_code == 200
    db_session.refresh(venta)

    # 7. CAJA - Cierre
    response = client.post("/admin/caja/cerrar", data={"monto_real": "70.00"}, follow_redirects=True)
    assert response.status_code == 200
    db_session.refresh(caja)
    assert caja.estado == EstadoCaja.cerrada

    # 8. LOGOUT
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200

    print("TEST E2E COMPLETO PASÓ CORRECTAMENTE")
