from decimal import Decimal

from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.admin import admin_bp
from app.admin.forms import (
    ActualizarDetallePedidoForm,
    ClienteForm,
    DetallePedidoForm,
    EstadoPedidoForm,
    PedidoForm,
    ProductoForm,
    UsuarioForm,
    VentaForm,
)
from app.auth.decorators import roles_required
from app.services import (
    CustomerService,
    OrderService,
    ProductService,
    SaleService,
    UserService,
)


@admin_bp.route("/usuarios")
@roles_required("administrador")
def list_users():
    service = UserService()
    return render_template("admin/users_list.html", users=service.list_users())


@admin_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@roles_required("administrador")
def create_user():
    form = UsuarioForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash("La contrasena es obligatoria al crear un usuario.", "danger")
            return render_template(
                "admin/user_form.html",
                form=form,
                page_title="Nuevo usuario",
                submit_label="Crear usuario",
            )
        service = UserService()
        try:
            service.create_user(
                full_name=form.nombre.data,
                username=form.usuario.data,
                password=form.password.data,
                role_name=form.rol.data,
                active=form.activo.data,
            )
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("admin.list_users"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template(
        "admin/user_form.html",
        form=form,
        page_title="Nuevo usuario",
        submit_label="Crear usuario",
    )


@admin_bp.route("/usuarios/<int:user_id>/editar", methods=["GET", "POST"])
@roles_required("administrador")
def edit_user(user_id: int):
    service = UserService()
    user = service.get_user(user_id)
    if user is None:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for("admin.list_users"))

    form = UsuarioForm(obj=user)
    if form.validate_on_submit():
        try:
            service.update_user(
                user=user,
                full_name=form.nombre.data,
                username=form.usuario.data,
                role_name=form.rol.data,
                active=form.activo.data,
                password=form.password.data or None,
            )
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("admin.list_users"))
        except ValueError as exc:
            flash(str(exc), "danger")
    elif not form.is_submitted():
        form.rol.data = user.role_name
        form.activo.data = user.activo

    return render_template(
        "admin/user_form.html",
        form=form,
        page_title="Editar usuario",
        submit_label="Actualizar usuario",
    )


@admin_bp.route("/usuarios/<int:user_id>/eliminar", methods=["POST"])
@roles_required("administrador")
def delete_user(user_id: int):
    service = UserService()
    user = service.get_user(user_id)
    if user is None:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for("admin.list_users"))

    try:
        service.delete_user(user, current_user.id)
        flash("Usuario eliminado correctamente.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/productos")
@roles_required("administrador")
def list_products():
    service = ProductService()
    return render_template("admin/products_list.html", products=service.list_products())


@admin_bp.route("/productos/nuevo", methods=["GET", "POST"])
@roles_required("administrador")
def create_product():
    form = ProductoForm()
    if form.validate_on_submit():
        service = ProductService()
        try:
            service.create_product(
                name=form.nombre.data,
                product_type=form.tipo.data,
                price=form.precio.data,
                available=form.disponible.data,
                customizable=form.es_personalizable.data,
            )
            flash("Producto creado correctamente.", "success")
            return redirect(url_for("admin.list_products"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template(
        "admin/product_form.html",
        form=form,
        page_title="Nuevo producto",
        submit_label="Crear producto",
    )


@admin_bp.route("/productos/<int:product_id>/editar", methods=["GET", "POST"])
@roles_required("administrador")
def edit_product(product_id: int):
    service = ProductService()
    product = service.get_product(product_id)
    if product is None:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("admin.list_products"))

    form = ProductoForm(obj=product)
    if form.validate_on_submit():
        try:
            service.update_product(
                product=product,
                name=form.nombre.data,
                product_type=form.tipo.data,
                price=form.precio.data,
                available=form.disponible.data,
                customizable=form.es_personalizable.data,
            )
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("admin.list_products"))
        except ValueError as exc:
            flash(str(exc), "danger")
    elif not form.is_submitted():
        form.tipo.data = product.tipo.value
        form.disponible.data = product.disponible
        form.es_personalizable.data = product.es_personalizable

    return render_template(
        "admin/product_form.html",
        form=form,
        page_title="Editar producto",
        submit_label="Actualizar producto",
    )


@admin_bp.route("/productos/<int:product_id>/eliminar", methods=["POST"])
@roles_required("administrador")
def delete_product(product_id: int):
    service = ProductService()
    product = service.get_product(product_id)
    if product is None:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("admin.list_products"))

    try:
        service.delete_product(product)
        flash("Producto eliminado correctamente.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.list_products"))


@admin_bp.route("/clientes")
@roles_required("administrador", "vendedor")
def list_customers():
    service = CustomerService()
    return render_template("admin/customers_list.html", customers=service.list_customers())


@admin_bp.route("/clientes/nuevo", methods=["GET", "POST"])
@roles_required("administrador", "vendedor")
def create_customer():
    form = ClienteForm()
    if form.validate_on_submit():
        service = CustomerService()
        try:
            service.create_customer(
                name=form.nombre.data,
                phone=form.telefono.data,
                address=form.direccion.data,
                reference=form.referencia.data,
            )
            flash("Cliente creado correctamente.", "success")
            return redirect(url_for("admin.list_customers"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template(
        "admin/customer_form.html",
        form=form,
        page_title="Nuevo cliente",
        submit_label="Crear cliente",
    )


@admin_bp.route("/clientes/<int:customer_id>/editar", methods=["GET", "POST"])
@roles_required("administrador", "vendedor")
def edit_customer(customer_id: int):
    service = CustomerService()
    customer = service.get_customer(customer_id)
    if customer is None:
        flash("Cliente no encontrado.", "warning")
        return redirect(url_for("admin.list_customers"))

    form = ClienteForm(obj=customer)
    if form.validate_on_submit():
        try:
            service.update_customer(
                customer=customer,
                name=form.nombre.data,
                phone=form.telefono.data,
                address=form.direccion.data,
                reference=form.referencia.data,
            )
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("admin.list_customers"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/customer_form.html",
        form=form,
        page_title="Editar cliente",
        submit_label="Actualizar cliente",
    )


@admin_bp.route("/clientes/<int:customer_id>/eliminar", methods=["POST"])
@roles_required("administrador", "vendedor")
def delete_customer(customer_id: int):
    service = CustomerService()
    customer = service.get_customer(customer_id)
    if customer is None:
        flash("Cliente no encontrado.", "warning")
        return redirect(url_for("admin.list_customers"))
    try:
        service.delete_customer(customer)
        flash("Cliente eliminado correctamente.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.list_customers"))


@admin_bp.route("/pedidos")
@roles_required("administrador", "vendedor", "cocina", "repartidor")
def list_orders():
    service = OrderService()
    orders = service.list_orders_for_user(current_user)
    return render_template("admin/orders_list.html", orders=orders)


@admin_bp.route("/pedidos/nuevo", methods=["GET", "POST"])
@roles_required("administrador", "vendedor")
def create_order():
    service = OrderService()
    customer_service = CustomerService()
    form = PedidoForm()
    form.cliente_id.choices = [
        (customer.id, f"{customer.nombre} - {customer.telefono}")
        for customer in customer_service.list_customers()
    ]
    form.repartidor_id.choices = [(0, "Sin asignar")] + [
        (user.id, user.nombre) for user in service.list_delivery_users()
    ]
    if form.validate_on_submit():
        try:
            order = service.create_order(
                customer_id=form.cliente_id.data,
                channel=form.canal.data,
                creator=current_user,
                address=form.direccion_entrega.data,
                notes=form.observaciones.data,
                delivery_user_id=form.repartidor_id.data or None,
            )
            flash("Pedido creado correctamente.", "success")
            return redirect(url_for("admin.order_detail", order_id=order.id))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template(
        "admin/order_form.html",
        form=form,
        page_title="Nuevo pedido",
        submit_label="Crear pedido",
    )


@admin_bp.route("/pedidos/<int:order_id>")
@roles_required("administrador", "vendedor", "cocina", "repartidor")
def order_detail(order_id: int):
    order_service = OrderService()
    sale_service = SaleService()
    try:
        order = order_service.get_order_or_raise_access(order_id, current_user)
    except PermissionError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.list_orders"))
    except ValueError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("admin.list_orders"))

    item_form = DetallePedidoForm()
    item_form.producto_id.choices = [
        (product.id, f"{product.nombre} - ${product.precio}")
        for product in order_service.available_products()
    ]
    status_form = EstadoPedidoForm()
    status_form.estado.data = order.estado.value
    sale_form = VentaForm()
    item_update_forms = {}
    for item in order.detalles:
        form = ActualizarDetallePedidoForm(prefix=f"item-{item.id}")
        form.cantidad.data = item.cantidad
        item_update_forms[item.id] = form

    return render_template(
        "admin/order_detail.html",
        order=order,
        order_subtotal=order_service.order_subtotal(order),
        item_form=item_form,
        item_update_forms=item_update_forms,
        status_form=status_form,
        sale_form=sale_form,
        sale=sale_service.get_sale_by_order_id(order.id),
    )


@admin_bp.route("/pedidos/<int:order_id>/editar", methods=["GET", "POST"])
@roles_required("administrador", "vendedor")
def edit_order(order_id: int):
    order_service = OrderService()
    customer_service = CustomerService()
    order = order_service.get_order(order_id)
    if order is None:
        flash("Pedido no encontrado.", "warning")
        return redirect(url_for("admin.list_orders"))

    form = PedidoForm(obj=order)
    form.cliente_id.choices = [
        (customer.id, f"{customer.nombre} - {customer.telefono}")
        for customer in customer_service.list_customers()
    ]
    form.repartidor_id.choices = [(0, "Sin asignar")] + [
        (user.id, user.nombre) for user in order_service.list_delivery_users()
    ]

    if form.validate_on_submit():
        try:
            order_service.update_order(
                order=order,
                customer_id=form.cliente_id.data,
                channel=form.canal.data,
                address=form.direccion_entrega.data,
                notes=form.observaciones.data,
                delivery_user_id=form.repartidor_id.data or None,
            )
            flash("Pedido actualizado correctamente.", "success")
            return redirect(url_for("admin.order_detail", order_id=order.id))
        except ValueError as exc:
            flash(str(exc), "danger")
    elif not form.is_submitted():
        form.cliente_id.data = order.cliente_id
        form.canal.data = order.canal.value
        form.direccion_entrega.data = order.direccion_entrega
        form.repartidor_id.data = order.repartidor_id or 0
        form.observaciones.data = order.observaciones

    return render_template(
        "admin/order_form.html",
        form=form,
        page_title="Editar pedido",
        submit_label="Actualizar pedido",
    )


@admin_bp.route("/pedidos/<int:order_id>/detalle/agregar", methods=["POST"])
@roles_required("administrador", "vendedor")
def add_order_item(order_id: int):
    order_service = OrderService()
    order = order_service.get_order(order_id)
    if order is None:
        flash("Pedido no encontrado.", "warning")
        return redirect(url_for("admin.list_orders"))

    form = DetallePedidoForm()
    form.producto_id.choices = [
        (product.id, f"{product.nombre} - ${product.precio}")
        for product in order_service.available_products()
    ]
    if form.validate_on_submit():
        try:
            order_service.add_order_item(
                order=order,
                product_id=form.producto_id.data,
                quantity=form.cantidad.data,
                extras=form.extras.data,
                notes=form.observaciones.data,
            )
            flash("Producto agregado al pedido.", "success")
        except ValueError as exc:
            flash(str(exc), "danger")
    else:
        flash("Datos invalidos para el detalle del pedido.", "danger")
    return redirect(url_for("admin.order_detail", order_id=order.id))


@admin_bp.route("/pedidos/<int:order_id>/detalle/<int:item_id>/actualizar", methods=["POST"])
@roles_required("administrador", "vendedor")
def update_order_item(order_id: int, item_id: int):
    order_service = OrderService()
    item = order_service.get_item(item_id)
    if item is None or item.pedido_id != order_id:
        flash("Detalle de pedido no encontrado.", "warning")
        return redirect(url_for("admin.order_detail", order_id=order_id))

    form = ActualizarDetallePedidoForm(prefix=f"item-{item.id}")
    if form.validate_on_submit():
        try:
            order_service.update_order_item(item, form.cantidad.data)
            flash("Detalle actualizado correctamente.", "success")
        except ValueError as exc:
            flash(str(exc), "danger")
    else:
        flash("Cantidad invalida.", "danger")
    return redirect(url_for("admin.order_detail", order_id=order_id))


@admin_bp.route("/pedidos/<int:order_id>/detalle/<int:item_id>/eliminar", methods=["POST"])
@roles_required("administrador", "vendedor")
def remove_order_item(order_id: int, item_id: int):
    order_service = OrderService()
    item = order_service.get_item(item_id)
    if item is None or item.pedido_id != order_id:
        flash("Detalle de pedido no encontrado.", "warning")
        return redirect(url_for("admin.order_detail", order_id=order_id))
    try:
        order_service.remove_order_item(item)
        flash("Producto eliminado del pedido.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.order_detail", order_id=order_id))


@admin_bp.route("/pedidos/<int:order_id>/estado", methods=["POST"])
@roles_required("administrador", "vendedor", "cocina", "repartidor")
def change_order_status(order_id: int):
    order_service = OrderService()
    order = order_service.get_order(order_id)
    if order is None:
        flash("Pedido no encontrado.", "warning")
        return redirect(url_for("admin.list_orders"))

    form = EstadoPedidoForm()
    if form.validate_on_submit():
        try:
            order_service.change_status(order, form.estado.data, current_user)
            flash("Estado actualizado correctamente.", "success")
        except (ValueError, PermissionError) as exc:
            flash(str(exc), "danger")
    else:
        flash("Estado invalido.", "danger")
    return redirect(url_for("admin.order_detail", order_id=order_id))


@admin_bp.route("/ventas")
@roles_required("administrador", "vendedor")
def list_sales():
    service = SaleService()
    return render_template("admin/sales_list.html", sales=service.list_sales())


@admin_bp.route("/pedidos/<int:order_id>/venta", methods=["GET", "POST"])
@roles_required("administrador", "vendedor")
def create_sale(order_id: int):
    order_service = OrderService()
    sale_service = SaleService()
    order = order_service.get_order(order_id)
    if order is None:
        flash("Pedido no encontrado.", "warning")
        return redirect(url_for("admin.list_orders"))

    existing_sale = sale_service.get_sale_by_order_id(order.id)
    if existing_sale is not None:
        flash("Este pedido ya tiene una venta registrada.", "warning")
        return redirect(url_for("admin.list_sales"))

    form = VentaForm()
    subtotal = order_service.order_subtotal(order)
    if form.validate_on_submit():
        try:
            sale_service.create_sale(
                order=order,
                seller=current_user,
                discount=form.descuento.data,
            )
            flash("Venta generada correctamente.", "success")
            return redirect(url_for("admin.list_sales"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "admin/sale_form.html",
        form=form,
        order=order,
        subtotal=subtotal,
        impuesto=(subtotal * Decimal("0.15")).quantize(Decimal("0.01")),
    )
