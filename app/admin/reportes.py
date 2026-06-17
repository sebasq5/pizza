from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request
from app.auth.decorators import roles_required
from app.models import RolNombre
from app.services.report_service import ReportService
from app.admin import admin_bp

@admin_bp.route("/reportes", methods=["GET"])
@roles_required(RolNombre.administrador.value)
def index():
    report_service = ReportService()
    
    # Parametros de fecha
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date_str = request.args.get("start_date", today_str)
    end_date_str = request.args.get("end_date", today_str)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") + timedelta(days=1)
    
    reporte_tipo = request.args.get("tipo", "ventas_fecha")
    
    data = None
    if reporte_tipo == "ventas_fecha":
        data = report_service.get_ventas_por_fecha(start_date, end_date)
    elif reporte_tipo == "ventas_producto":
        data = report_service.get_ventas_por_producto()
    elif reporte_tipo == "pedidos_estado":
        data = report_service.get_pedidos_por_estado()
    elif reporte_tipo == "inventario":
        data = report_service.get_inventario_actual()
    elif reporte_tipo == "mas_vendidos":
        data = report_service.get_productos_mas_vendidos()
    elif reporte_tipo == "caja_diaria":
        data = report_service.get_caja_diaria(start_date_str)
    elif reporte_tipo == "movimientos":
        data = report_service.get_movimientos_inventario(fecha_inicio=start_date, fecha_fin=end_date)
        
    return render_template(
        "admin/reportes/index.html",
        reporte_tipo=reporte_tipo,
        start_date=start_date_str,
        end_date=end_date_str,
        data=data
    )
