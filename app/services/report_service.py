from app.extensions import db
from sqlalchemy import func
from app.models import Venta, Pedido, DetallePedido, Producto, MovimientoInventario, Caja
from datetime import datetime

class ReportService:
    def get_ventas_por_fecha(self, start_date, end_date):
        query = db.session.query(
            func.date(Venta.fecha_venta).label('fecha'),
            func.count(Venta.id).label('cantidad_ventas'),
            func.sum(Venta.total).label('total')
        ).filter(
            Venta.fecha_venta >= start_date,
            Venta.fecha_venta <= end_date
        ).group_by(func.date(Venta.fecha_venta)).order_by('fecha').all()
        return query

    def get_ventas_por_producto(self):
        query = db.session.query(
            Producto.nombre,
            func.sum(DetallePedido.cantidad).label('cantidad_vendida'),
            func.sum(DetallePedido.subtotal).label('total_generado')
        ).join(DetallePedido, Producto.id == DetallePedido.producto_id) \
         .join(Pedido, Pedido.id == DetallePedido.pedido_id) \
         .join(Venta, Venta.pedido_id == Pedido.id) \
         .group_by(Producto.id).order_by(func.sum(DetallePedido.cantidad).desc()).all()
        return query

    def get_pedidos_por_estado(self):
        query = db.session.query(
            Pedido.estado,
            func.count(Pedido.id).label('cantidad')
        ).group_by(Pedido.estado).all()
        return query

    def get_inventario_actual(self):
        from app.models import Ingrediente
        return Ingrediente.query.order_by(Ingrediente.nombre).all()

    def get_productos_mas_vendidos(self):
        # Mismo query que ventas_por_producto, pero limitado
        return self.get_ventas_por_producto()

    def get_caja_diaria(self, date):
        return db.session.query(Caja).filter(func.date(Caja.fecha_apertura) == date).all()

    def get_movimientos_inventario(self, ingrediente_id=None, motivo=None, fecha_inicio=None, fecha_fin=None):
        query = MovimientoInventario.query
        if ingrediente_id:
            query = query.filter_by(ingrediente_id=ingrediente_id)
        if motivo:
            query = query.filter_by(motivo=motivo)
        if fecha_inicio:
            query = query.filter(MovimientoInventario.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(MovimientoInventario.fecha <= fecha_fin)
            
        return query.order_by(MovimientoInventario.fecha.desc()).all()

    def get_dashboard_metrics(self):
        today = datetime.utcnow().date()
        
        # Ventas del día (total)
        ventas_hoy = db.session.query(func.sum(Venta.total)).filter(
            func.date(Venta.fecha_venta) == today
        ).scalar() or 0
        
        # Pedidos pendientes
        from app.models import EstadoPedido
        pedidos_pendientes = Pedido.query.filter_by(estado=EstadoPedido.pendiente).count()
        
        # Productos bajo stock (ingredientes)
        from app.models import Ingrediente
        bajo_stock = Ingrediente.query.filter(Ingrediente.stock_actual <= Ingrediente.stock_minimo).count()
        
        # Cajas abiertas
        from app.models import EstadoCaja
        cajas_abiertas = Caja.query.filter_by(estado=EstadoCaja.abierta).count()
        
        # Últimas ventas
        ultimas_ventas = Venta.query.order_by(Venta.fecha_venta.desc()).limit(5).all()
        
        return {
            "ventas_hoy": ventas_hoy,
            "pedidos_pendientes": pedidos_pendientes,
            "bajo_stock": bajo_stock,
            "cajas_abiertas": cajas_abiertas,
            "ultimas_ventas": ultimas_ventas
        }
