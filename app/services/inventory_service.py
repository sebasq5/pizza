from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import (
    DetallePedido,
    EstadoVenta,
    Ingrediente,
    MotivoMovimiento,
    MovimientoInventario,
    Receta,
    TipoMovimiento,
    Usuario,
    Venta,
)
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.movimiento_inventario_repository import MovimientoInventarioRepository
from app.repositories.receta_repository import RecetaRepository
from app.services.audit_service import AuditService


class InventoryService:
    def __init__(
        self,
        ingrediente_repo: IngredienteRepository | None = None,
        receta_repo: RecetaRepository | None = None,
        movimiento_repo: MovimientoInventarioRepository | None = None,
    ) -> None:
        self.ingrediente_repo = ingrediente_repo or IngredienteRepository()
        self.receta_repo = receta_repo or RecetaRepository()
        self.movimiento_repo = movimiento_repo or MovimientoInventarioRepository()
        self.audit_service = AuditService()

    # --- INGREDIENTES ---
    def list_ingredientes(self):
        return self.ingrediente_repo.get_all()

    def get_ingrediente(self, ingrediente_id: int):
        return self.ingrediente_repo.get_by_id(ingrediente_id)

    def create_ingrediente(self, ingrediente: Ingrediente):
        return self.ingrediente_repo.create(ingrediente)

    # --- RECETAS ---
    def get_recetas_por_producto(self, producto_id: int):
        return self.receta_repo.get_by_producto_id(producto_id)

    def add_ingrediente_a_producto(self, producto_id: int, ingrediente_id: int, cantidad: float):
        receta = Receta(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            cantidad=cantidad,
        )
        return self.receta_repo.create(receta)

    def remove_ingrediente_de_producto(self, receta_id: int):
        receta = self.receta_repo.get_by_id(receta_id)
        if receta:
            self.receta_repo.delete(receta)

    # --- MOVIMIENTOS ---
    def register_movimiento(
        self,
        ingrediente_id: int,
        tipo: TipoMovimiento,
        motivo: MotivoMovimiento,
        cantidad: float,
        responsable_id: int,
    ):
        if cantidad <= 0:
            raise ValueError("La cantidad del movimiento debe ser mayor a 0")
        
        movimiento = MovimientoInventario(
            ingrediente_id=ingrediente_id,
            tipo=tipo,
            motivo=motivo,
            cantidad=cantidad,
            responsable_id=responsable_id,
        )
        self.movimiento_repo.create(movimiento)

        ingrediente = self.ingrediente_repo.get_by_id(ingrediente_id)
        if tipo == TipoMovimiento.entrada:
            ingrediente.stock_actual += Decimal(str(cantidad))
        elif tipo == TipoMovimiento.salida:
            ingrediente.stock_actual -= Decimal(str(cantidad))
            if ingrediente.stock_actual < 0:
                raise ValueError(f"Stock insuficiente para el ingrediente: {ingrediente.nombre}")
        elif tipo == TipoMovimiento.ajuste:
            # We assume adjustment provides the new exact stock or difference?
            # "ajuste" in TipoMovimiento usually means we manually fix stock. Let's make it additive for now
            # if we want absolute, we need to pass absolute. The prompt says "ajuste" + "cantidad". 
            # I will assume "ajuste" type means an adjustment of stock, so we add the amount (could be pos or neg). 
            # Wait, the rule says `cantidad > 0`. If adjustment is negative, how to represent it?
            # Usually we use "salida" con motivo "ajuste_manual" for negative adjustment, and "entrada" for positive.
            pass

        self.audit_service.log_action(
            usuario_id=responsable_id,
            accion="movimientos inventario",
            tabla_afectada="movimientos_inventario",
            registro_id=movimiento.id,
            detalle=f"{tipo.value.capitalize()} de {cantidad} para {ingrediente.nombre}"
        )

        return movimiento

    # --- OPERACIONES DE VENTA ---
    def _calcular_consumo_venta(self, venta: Venta) -> dict[int, Decimal]:
        """Calcula el consumo total de ingredientes para una venta."""
        consumo = {}
        for detalle in venta.pedido.detalles:
            recetas = self.get_recetas_por_producto(detalle.producto_id)
            for receta in recetas:
                ingrediente_id = receta.ingrediente_id
                cantidad_total = Decimal(str(receta.cantidad)) * detalle.cantidad
                if ingrediente_id in consumo:
                    consumo[ingrediente_id] += cantidad_total
                else:
                    consumo[ingrediente_id] = cantidad_total
        return consumo

    def validar_stock_venta(self, venta: Venta):
        """Verifica si hay stock suficiente para todos los ingredientes."""
        consumo = self._calcular_consumo_venta(venta)
        for ingrediente_id, cantidad_requerida in consumo.items():
            ingrediente = self.ingrediente_repo.get_by_id(ingrediente_id)
            if ingrediente.stock_actual < cantidad_requerida:
                raise ValueError(
                    f"Stock insuficiente de '{ingrediente.nombre}'. "
                    f"Requerido: {cantidad_requerida}, Actual: {ingrediente.stock_actual}"
                )

    def descontar_inventario_venta(self, venta: Venta, responsable_id: int):
        """Descuenta el inventario y crea movimientos. Debe llamarse dentro de una transacción."""
        self.validar_stock_venta(venta)
        consumo = self._calcular_consumo_venta(venta)

        for ingrediente_id, cantidad in consumo.items():
            movimiento = MovimientoInventario(
                ingrediente_id=ingrediente_id,
                tipo=TipoMovimiento.salida,
                motivo=MotivoMovimiento.venta,
                cantidad=cantidad,
                responsable_id=responsable_id,
            )
            self.movimiento_repo.create(movimiento)
            
            ingrediente = self.ingrediente_repo.get_by_id(ingrediente_id)
            ingrediente.stock_actual -= cantidad

    def revertir_inventario_venta(self, venta: Venta, responsable_id: int):
        """Revierte el inventario y crea movimientos de cancelación. Debe llamarse dentro de una transacción."""
        consumo = self._calcular_consumo_venta(venta)

        for ingrediente_id, cantidad in consumo.items():
            movimiento = MovimientoInventario(
                ingrediente_id=ingrediente_id,
                tipo=TipoMovimiento.entrada,
                motivo=MotivoMovimiento.cancelacion,
                cantidad=cantidad,
                responsable_id=responsable_id,
            )
            self.movimiento_repo.create(movimiento)
            
            ingrediente = self.ingrediente_repo.get_by_id(ingrediente_id)
            ingrediente.stock_actual += cantidad
