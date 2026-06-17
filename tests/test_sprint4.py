import pytest
from app.models import Usuario, Caja, EstadoCaja, Auditoria, MetodoPago
from decimal import Decimal
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def sqlite_engine_connect(dbapi_connection, connection_record):
    if type(dbapi_connection).__name__ == "Connection":
        try:
            dbapi_connection.create_function("btrim", 1, lambda x: x.strip() if x else x)
        except AttributeError:
            pass

from app import create_app
from app.extensions import bcrypt, db
from app.models import Usuario, Caja, EstadoCaja, Auditoria, MetodoPago, Rol, RolNombre

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
            nombre="Test User",
            usuario="testuser",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            rol=roles["administrador"],
            activo=True,
        )
        db.session.add(test_user)
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

@pytest.fixture()
def test_user(app, db_session):
    return db_session.query(Usuario).filter_by(usuario="testuser").first()

def test_apertura_caja_success(client, db_session, test_user):
    # Asegurarse que es administrador
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    # Intentar abrir caja
    response = client.post("/admin/caja/abrir", data={"monto_apertura": "100.00"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Caja abierta exitosamente" in response.data
    
    # Verificar en BD
    caja = db_session.query(Caja).filter_by(usuario_id=test_user.id, estado=EstadoCaja.abierta).first()
    assert caja is not None
    assert caja.monto_apertura == Decimal("100.00")
    
    # Verificar Auditoría
    auditoria = db_session.query(Auditoria).filter_by(accion="apertura caja").first()
    assert auditoria is not None
    assert auditoria.usuario_id == test_user.id

def test_apertura_caja_duplicate(client, db_session, test_user):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    # Abrir primera caja
    client.post("/admin/caja/abrir", data={"monto_apertura": "100.00"})
    
    # Intentar abrir segunda caja
    response = client.post("/admin/caja/abrir", data={"monto_apertura": "50.00"}, follow_redirects=True)
    assert b"Ya tienes una caja abierta" in response.data

def test_cierre_caja(client, db_session, test_user):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    # Abrir caja
    client.post("/admin/caja/abrir", data={"monto_apertura": "100.00"})
    
    # Cerrar caja (con un faltante)
    response = client.post("/admin/caja/cerrar", data={"monto_real": "90.00"}, follow_redirects=True)
    assert b"Caja cerrada con FALTANTE" in response.data
    
    # Verificar BD
    caja = db_session.query(Caja).filter_by(usuario_id=test_user.id).order_by(Caja.id.desc()).first()
    assert caja.estado == EstadoCaja.cerrada
    assert caja.monto_esperado == Decimal("100.00")
    assert caja.diferencia == Decimal("-10.00")
    
    # Verificar Auditoría
    auditoria = db_session.query(Auditoria).filter_by(accion="cierre caja").first()
    assert auditoria is not None

def test_registro_pago_con_caja_cerrada_falla(client, db_session, test_user):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    # Ensure there is no open box
    caja = db_session.query(Caja).filter_by(usuario_id=test_user.id, estado=EstadoCaja.abierta).first()
    if caja:
        caja.estado = EstadoCaja.cerrada
        db_session.commit()
        
    # Necesitamos una venta para pagar, pero podemos probar el servicio directamente o mockear
    from app.services.payment_service import PaymentService
    from app.models import Venta, EstadoVenta
    
    # Crea venta dummy
    # Para evitar crear todo el grafo, es mejor validar la logica en el servicio
    service = PaymentService()
    
    try:
        # Mock venta
        class MockVenta:
            estado = EstadoVenta.registrada
            id = 1
            
        service.register_pago(MockVenta(), MetodoPago.efectivo, Decimal("10.00"), test_user)
        assert False, "Debería haber fallado porque no hay caja abierta"
    except ValueError as e:
        assert str(e) == "No se puede registrar el pago: debe abrir la caja primero."

def test_reportes_acceso_administrador(client, test_user):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    response = client.get("/admin/reportes")
    assert response.status_code == 200
    assert b"Reportes Administrativos" in response.data
    assert b"Ventas por Fecha" in response.data

def test_auditoria_login_registrado(client, db_session, test_user):
    client.post("/login", data={"username": "testuser", "password": "password123"})
    
    # Verificar que el login se registró en auditoría
    auditoria = db_session.query(Auditoria).filter_by(usuario_id=test_user.id, accion="login").first()
    assert auditoria is not None
    assert "Inicio de sesión exitoso" in auditoria.detalle
