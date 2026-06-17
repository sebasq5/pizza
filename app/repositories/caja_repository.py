from app.models import Caja, EstadoCaja
from app.extensions import db

class CajaRepository:
    def get_by_id(self, caja_id):
        return Caja.query.get(caja_id)

    def get_all(self):
        return Caja.query.order_by(Caja.fecha_apertura.desc()).all()

    def get_active_box_for_user(self, usuario_id):
        return Caja.query.filter_by(usuario_id=usuario_id, estado=EstadoCaja.abierta).first()

    def get_all_active_boxes(self):
        return Caja.query.filter_by(estado=EstadoCaja.abierta).all()

    def create(self, caja_data):
        caja = Caja(**caja_data)
        db.session.add(caja)
        return caja

    def get_daily_boxes(self, date):
        # Filtra cajas cuya fecha de apertura coincida con el dia
        return Caja.query.filter(db.func.date(Caja.fecha_apertura) == date).all()
