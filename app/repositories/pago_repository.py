from typing import Sequence

from app.extensions import db
from app.models.pago import Pago


class PagoRepository:
    def create(self, pago: Pago) -> Pago:
        db.session.add(pago)
        return pago

    def get_by_id(self, pago_id: int) -> Pago | None:
        return db.session.get(Pago, pago_id)

    def get_by_venta_id(self, venta_id: int) -> Sequence[Pago]:
        return db.session.scalars(db.select(Pago).filter_by(venta_id=venta_id)).all()

    def get_pagos_by_user_and_date_range(self, usuario_id: int, start_date, end_date=None) -> Sequence[Pago]:
        query = db.select(Pago).filter(
            Pago.responsable_id == usuario_id,
            Pago.fecha >= start_date
        )
        if end_date:
            query = query.filter(Pago.fecha <= end_date)
        return db.session.scalars(query).all()
