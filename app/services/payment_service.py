from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import EstadoVenta, MetodoPago, Pago, Usuario, Venta
from app.repositories.pago_repository import PagoRepository
from app.repositories.venta_repository import VentaRepository
from app.services.inventory_service import InventoryService
from app.services.caja_service import CajaService
from app.services.audit_service import AuditService


class PaymentService:
    def __init__(
        self,
        pago_repo: PagoRepository | None = None,
        venta_repo: VentaRepository | None = None,
        inventory_service: InventoryService | None = None,
    ) -> None:
        self.pago_repo = pago_repo or PagoRepository()
        self.venta_repo = venta_repo or VentaRepository()
        self.inventory_service = inventory_service or InventoryService()
        self.caja_service = CajaService()
        self.audit_service = AuditService()

    def register_pago(
        self,
        venta: Venta,
        metodo: MetodoPago,
        monto: Decimal,
        responsable: Usuario,
        referencia: str | None = None,
    ) -> Pago:
        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0.")
        
        if not self.caja_service.is_box_open(responsable.id):
            raise ValueError("No se puede registrar el pago: debe abrir la caja primero.")
            
        if venta.estado == EstadoVenta.anulada:
            raise ValueError("No se pueden registrar pagos sobre una venta anulada.")

        if metodo in (MetodoPago.transferencia, MetodoPago.tarjeta):
            if not referencia or not referencia.strip():
                raise ValueError(f"La referencia es obligatoria para pagos con {metodo.value}.")

        # Before registering payment, validate if this payment will fully pay the sale
        # If it fully pays, we must validate stock BEFORE registering anything to avoid partial state
        pagos_existentes = self.pago_repo.get_by_venta_id(venta.id)
        total_pagado = sum(Decimal(str(p.monto)) for p in pagos_existentes) + monto
        
        se_pagara_completamente = total_pagado >= Decimal(str(venta.total))
        
        if se_pagara_completamente and venta.estado != EstadoVenta.pagada:
            # Validate stock. Will raise exception if not enough stock.
            self.inventory_service.validar_stock_venta(venta)

        pago = Pago(
            venta_id=venta.id,
            metodo=metodo,
            monto=monto,
            referencia=referencia,
            responsable_id=responsable.id,
        )
        self.pago_repo.create(pago)

        try:
            db.session.flush()

            if se_pagara_completamente and venta.estado != EstadoVenta.pagada:
                # Transition to pagada
                venta.estado = EstadoVenta.pagada
                self.inventory_service.descontar_inventario_venta(venta, responsable.id)

            self.audit_service.log_action(
                usuario_id=responsable.id,
                accion="registro pago",
                tabla_afectada="pagos",
                registro_id=pago.id,
                detalle=f"Abono de ${monto} a la venta #{venta.id}"
            )

            db.session.commit()
            return pago
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("Error al registrar el pago en la base de datos.") from exc
        except Exception as exc:
            db.session.rollback()
            raise ValueError(str(exc)) from exc
