from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.admin.forms import IngredienteForm, MovimientoInventarioForm, RecetaForm
from app.auth.decorators import roles_required
from app.services.inventory_service import InventoryService
from app.services.product_service import ProductService


@admin_bp.route("/inventario/ingredientes")
@roles_required("administrador", "bodeguero", "vendedor")
def list_ingredientes():
    service = InventoryService()
    return render_template("admin/inventario/ingredientes_list.html", ingredientes=service.list_ingredientes())


@admin_bp.route("/inventario/ingredientes/nuevo", methods=["GET", "POST"])
@roles_required("administrador", "bodeguero")
def create_ingrediente():
    form = IngredienteForm()
    if form.validate_on_submit():
        service = InventoryService()
        try:
            from app.models.ingrediente import Ingrediente, UnidadMedida
            ing = Ingrediente(
                nombre=form.nombre.data,
                unidad_medida=UnidadMedida(form.unidad_medida.data),
                stock_actual=form.stock_actual.data,
                stock_minimo=form.stock_minimo.data,
                activo=form.activo.data
            )
            service.create_ingrediente(ing)
            flash("Ingrediente creado.", "success")
            return redirect(url_for("admin.list_ingredientes"))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("admin/inventario/ingrediente_form.html", form=form, title="Nuevo Ingrediente")


@admin_bp.route("/inventario/movimientos")
@roles_required("administrador", "bodeguero")
def list_movimientos():
    service = InventoryService()
    movimientos = service.movimiento_repo.get_all()
    return render_template("admin/inventario/movimientos_list.html", movimientos=movimientos)


@admin_bp.route("/inventario/movimientos/nuevo", methods=["GET", "POST"])
@roles_required("administrador", "bodeguero")
def create_movimiento():
    form = MovimientoInventarioForm()
    service = InventoryService()
    
    form.ingrediente_id.choices = [
        (ing.id, ing.nombre) for ing in service.list_ingredientes()
    ]
    
    if form.validate_on_submit():
        try:
            from app.models.movimiento_inventario import TipoMovimiento, MotivoMovimiento
            service.register_movimiento(
                ingrediente_id=form.ingrediente_id.data,
                tipo=TipoMovimiento(form.tipo.data),
                motivo=MotivoMovimiento(form.motivo.data),
                cantidad=form.cantidad.data,
                responsable_id=current_user.id
            )
            flash("Movimiento registrado correctamente.", "success")
            return redirect(url_for("admin.list_movimientos"))
        except ValueError as exc:
            flash(str(exc), "danger")
    
    return render_template("admin/inventario/movimiento_form.html", form=form)


@admin_bp.route("/productos/<int:product_id>/receta", methods=["GET", "POST"])
@roles_required("administrador", "bodeguero")
def manage_receta(product_id: int):
    prod_service = ProductService()
    inv_service = InventoryService()
    
    product = prod_service.get_product(product_id)
    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("admin.list_products"))
        
    form = RecetaForm()
    form.ingrediente_id.choices = [
        (ing.id, f"{ing.nombre} ({ing.unidad_medida.value})") 
        for ing in inv_service.list_ingredientes()
    ]
    
    if form.validate_on_submit():
        try:
            inv_service.add_ingrediente_a_producto(
                producto_id=product.id,
                ingrediente_id=form.ingrediente_id.data,
                cantidad=form.cantidad.data
            )
            flash("Ingrediente agregado a la receta.", "success")
            return redirect(url_for("admin.manage_receta", product_id=product.id))
        except Exception as exc:
            flash(str(exc), "danger")
            
    recetas = inv_service.get_recetas_por_producto(product.id)
    return render_template("admin/inventario/receta_manage.html", product=product, form=form, recetas=recetas)

@admin_bp.route("/recetas/<int:receta_id>/eliminar", methods=["POST"])
@roles_required("administrador", "bodeguero")
def delete_receta(receta_id: int):
    inv_service = InventoryService()
    receta = inv_service.receta_repo.get_by_id(receta_id)
    if receta:
        prod_id = receta.producto_id
        inv_service.remove_ingrediente_de_producto(receta_id)
        flash("Ingrediente eliminado de la receta.", "success")
        return redirect(url_for("admin.manage_receta", product_id=prod_id))
    flash("Receta no encontrada.", "danger")
    return redirect(url_for("admin.list_products"))
