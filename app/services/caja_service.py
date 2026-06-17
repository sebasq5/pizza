from datetime import datetime, timezone
from app.repositories.caja_repository import CajaRepository
from app.repositories.pago_repository import PagoRepository
from app.models.caja import EstadoCaja
from app.extensions import db
from app.services.audit_service import AuditService

class CajaService:
    def __init__(self):
        self.caja_repository = CajaRepository()
        self.pago_repository = PagoRepository()
        self.audit_service = AuditService()

    def get_caja(self, caja_id):
        return self.caja_repository.get_by_id(caja_id)

    def get_cajas_diarias(self, date):
        return self.caja_repository.get_daily_boxes(date)

    def get_active_box(self, usuario_id):
        return self.caja_repository.get_active_box_for_user(usuario_id)

    def is_box_open(self, usuario_id):
        return self.get_active_box(usuario_id) is not None

    def abrir_caja(self, usuario_id, monto_apertura):
        if self.is_box_open(usuario_id):
            raise ValueError("El usuario ya tiene una caja abierta.")
            
        if monto_apertura < 0:
            raise ValueError("El monto de apertura no puede ser negativo.")

        data = {
            "usuario_id": usuario_id,
            "monto_apertura": monto_apertura,
            "estado": EstadoCaja.abierta,
            "fecha_apertura": datetime.now(timezone.utc)
        }
        
        caja = self.caja_repository.create(data)
        
        self.audit_service.log_action(
            usuario_id=usuario_id,
            accion="apertura caja",
            tabla_afectada="cajas",
            detalle=f"Apertura con monto ${monto_apertura}"
        )
        
        db.session.commit()
        return caja

    def calcular_totales(self, caja):
        """
        Calcula los totales de efectivo, tarjetas, y transferencias
        registrados por el usuario desde que abrió la caja.
        """
        from app.models.pago import MetodoPago
        
        # Pagos del usuario desde la fecha de apertura
        pagos = self.pago_repository.get_pagos_by_user_and_date_range(
            caja.usuario_id,
            caja.fecha_apertura,
            caja.fecha_cierre
        )
        
        total_efectivo = sum(p.monto for p in pagos if p.metodo == MetodoPago.efectivo)
        total_tarjetas = sum(p.monto for p in pagos if p.metodo == MetodoPago.tarjeta)
        total_transferencias = sum(p.monto for p in pagos if p.metodo == MetodoPago.transferencia)
        
        monto_esperado = caja.monto_apertura + total_efectivo
        
        return {
            "total_efectivo": total_efectivo,
            "total_tarjetas": total_tarjetas,
            "total_transferencias": total_transferencias,
            "total_pagos": total_efectivo + total_tarjetas + total_transferencias,
            "monto_esperado": monto_esperado
        }

    def cerrar_caja(self, caja_id, usuario_id, monto_real):
        caja = self.get_caja(caja_id)
        if not caja:
            raise ValueError("Caja no encontrada.")
            
        if caja.usuario_id != usuario_id:
            raise ValueError("Solo el usuario responsable puede cerrar su caja.")
            
        if caja.estado == EstadoCaja.cerrada:
            raise ValueError("No se puede modificar una caja ya cerrada.")
            
        if monto_real < 0:
            raise ValueError("El monto real no puede ser negativo.")

        caja.fecha_cierre = datetime.now(timezone.utc)
        
        totales = self.calcular_totales(caja)
        caja.monto_esperado = totales["monto_esperado"]
        caja.monto_real = monto_real
        caja.diferencia = monto_real - caja.monto_esperado
        caja.estado = EstadoCaja.cerrada
        
        self.audit_service.log_action(
            usuario_id=usuario_id,
            accion="cierre caja",
            tabla_afectada="cajas",
            registro_id=caja.id,
            detalle=f"Diferencia calculada: ${caja.diferencia}"
        )
        
        db.session.commit()
        return caja
