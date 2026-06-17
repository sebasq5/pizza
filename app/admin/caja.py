from datetime import datetime, timezone
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from app.admin.forms import CajaAperturaForm, CajaCierreForm
from app.auth.decorators import roles_required
from app.models import RolNombre
from app.services.caja_service import CajaService
from app.admin import admin_bp

@admin_bp.route("/caja", methods=["GET"])
@roles_required(RolNombre.administrador.value, RolNombre.cajero.value)
def list_cajas():
    caja_service = CajaService()
    date_str = request.args.get("fecha", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    cajas = caja_service.get_cajas_diarias(date_str)
    
    active_box = caja_service.get_active_box(current_user.id)
    
    return render_template(
        "admin/caja/cajas_list.html", 
        cajas=cajas, 
        active_box=active_box,
        selected_date=date_str
    )

@admin_bp.route("/caja/abrir", methods=["GET", "POST"])
@roles_required(RolNombre.administrador.value, RolNombre.cajero.value)
def abrir_caja():
    caja_service = CajaService()
    
    if caja_service.is_box_open(current_user.id):
        flash("Ya tienes una caja abierta.", "warning")
        return redirect(url_for("admin.list_cajas"))
        
    form = CajaAperturaForm()
    if form.validate_on_submit():
        try:
            caja_service.abrir_caja(current_user.id, form.monto_apertura.data)
            flash("Caja abierta exitosamente.", "success")
            return redirect(url_for("admin.list_cajas"))
        except ValueError as e:
            flash(str(e), "danger")
            
    return render_template("admin/caja/caja_abrir.html", form=form)

@admin_bp.route("/caja/cerrar", methods=["GET", "POST"])
@roles_required(RolNombre.administrador.value, RolNombre.cajero.value)
def cerrar_caja():
    caja_service = CajaService()
    active_box = caja_service.get_active_box(current_user.id)
    
    if not active_box:
        flash("No tienes una caja abierta para cerrar.", "warning")
        return redirect(url_for("admin.list_cajas"))
        
    totales = caja_service.calcular_totales(active_box)
    
    form = CajaCierreForm()
    if form.validate_on_submit():
        try:
            caja = caja_service.cerrar_caja(active_box.id, current_user.id, form.monto_real.data)
            
            if caja.diferencia > 0:
                flash(f"Caja cerrada con SOBRANTE de ${caja.diferencia}", "warning")
            elif caja.diferencia < 0:
                flash(f"Caja cerrada con FALTANTE de ${abs(caja.diferencia)}", "danger")
            else:
                flash("Caja cerrada cuadrada perfectamente.", "success")
                
            return redirect(url_for("admin.list_cajas"))
        except ValueError as e:
            flash(str(e), "danger")
            
    return render_template("admin/caja/caja_cerrar.html", form=form, active_box=active_box, totales=totales)
