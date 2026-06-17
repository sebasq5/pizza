from flask import request
from app.repositories.auditoria_repository import AuditoriaRepository
from app.extensions import db

class AuditService:
    def __init__(self):
        self.repository = AuditoriaRepository()

    def log_action(self, usuario_id=None, accion=None, tabla_afectada=None, registro_id=None, detalle=None):
        # Intentar capturar la IP y el usuario si estamos en un contexto web
        ip_origen = None
        try:
            if request:
                ip_origen = request.remote_addr
                if not usuario_id:
                    from flask_login import current_user
                    if current_user and current_user.is_authenticated:
                        usuario_id = current_user.id
        except Exception:
            pass

        data = {
            "usuario_id": usuario_id,
            "accion": accion,
            "tabla_afectada": tabla_afectada,
            "registro_id": registro_id,
            "detalle": detalle,
            "ip_origen": ip_origen
        }
        
        registro = self.repository.create(data)
        return registro
