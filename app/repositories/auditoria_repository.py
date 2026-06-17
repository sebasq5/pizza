from app.models import Auditoria
from app.extensions import db

class AuditoriaRepository:
    def get_all(self):
        return Auditoria.query.order_by(Auditoria.fecha.desc()).all()

    def create(self, auditoria_data):
        registro = Auditoria(**auditoria_data)
        db.session.add(registro)
        return registro

    def filter_by(self, usuario_id=None, accion=None, tabla=None, fecha_inicio=None, fecha_fin=None):
        query = Auditoria.query

        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        if accion:
            query = query.filter(Auditoria.accion.ilike(f"%{accion}%"))
        if tabla:
            query = query.filter_by(tabla_afectada=tabla)
        if fecha_inicio:
            query = query.filter(Auditoria.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Auditoria.fecha <= fecha_fin)

        return query.order_by(Auditoria.fecha.desc()).all()
