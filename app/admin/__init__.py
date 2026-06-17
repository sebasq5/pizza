from flask import Blueprint

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from app.admin import routes
from app.admin import inventario
from app.admin import pagos
from app.admin import caja
from app.admin import auditoria
from app.admin import reportes
