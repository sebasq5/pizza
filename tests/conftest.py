import pytest
from app import create_app
from app.extensions import bcrypt, db
from app.models import Usuario, Rol, RolNombre
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Compatibilidad con btrim de Postgres en SQLite para tests
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
def db(db_session):
    return db_session

@pytest.fixture()
def test_user(app, db_session):
    return db_session.query(Usuario).filter_by(usuario="testuser").first()
