from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request
from app.auth.decorators import roles_required
from app.models import RolNombre
from app.repositories.auditoria_repository import AuditoriaRepository
from app.admin import admin_bp

@admin_bp.route("/auditoria", methods=["GET"])
@roles_required(RolNombre.administrador.value)
def list_auditoria():
    repo = AuditoriaRepository()
    
    fecha_str = request.args.get("fecha", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d")
    fecha_fin = fecha_inicio + timedelta(days=1)
    
    accion = request.args.get("accion", "")
    tabla = request.args.get("tabla", "")
    
    registros = repo.filter_by(
        accion=accion if accion else None,
        tabla=tabla if tabla else None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    
    return render_template(
        "admin/auditoria/auditoria_list.html",
        registros=registros,
        selected_date=fecha_str,
        selected_accion=accion,
        selected_tabla=tabla
    )
