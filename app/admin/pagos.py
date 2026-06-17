from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.admin.forms import PagoForm
from app.auth.decorators import roles_required
from app.services.payment_service import PaymentService
from app.services.sale_service import SaleService


@admin_bp.route("/ventas/<int:venta_id>/pagar", methods=["GET", "POST"])
@roles_required("administrador", "cajero")
def register_pago(venta_id: int):
    sale_service = SaleService()
    payment_service = PaymentService()
    
    venta = sale_service.get_sale_by_order_id(venta_id) # Wait, it's by order_id? No, sale_service doesn't have get_sale_by_id!
    # Let me check sale_service. Yes, it has get_sale_by_order_id but not get_sale by id. 
    # I should use sale_repository.get_by_id directly or add get_sale to SaleService.
    # Actually I can just get it via sale_repository.
    venta = sale_service.sale_repository.get_by_id(venta_id)
    if not venta:
        flash("Venta no encontrada.", "danger")
        return redirect(url_for("admin.list_sales"))
        
    form = PagoForm()
    if form.validate_on_submit():
        try:
            from app.models.pago import MetodoPago
            payment_service.register_pago(
                venta=venta,
                metodo=MetodoPago(form.metodo.data),
                monto=form.monto.data,
                responsable=current_user,
                referencia=form.referencia.data
            )
            flash("Pago registrado con éxito.", "success")
            return redirect(url_for("admin.list_sales"))
        except ValueError as exc:
            flash(str(exc), "danger")
            
    pagos = payment_service.pago_repo.get_by_venta_id(venta.id)
    return render_template("admin/pagos/pago_form.html", form=form, venta=venta, pagos=pagos)

@admin_bp.route("/pagos")
@roles_required("administrador", "cajero")
def list_pagos():
    from app.models.pago import Pago
    from app.extensions import db
    pagos = db.session.scalars(db.select(Pago).order_by(Pago.fecha.desc())).all()
    return render_template("admin/pagos/pagos_list.html", pagos=pagos)
