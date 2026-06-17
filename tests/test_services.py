import pytest
from decimal import Decimal
from app.models import (
    Cliente, Producto, Pedido, DetallePedido, 
    EstadoPedido, CanalPedido, ProductoTipo
)
from app.services.order_service import OrderService
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService
from app.services.user_service import UserService

def test_customer_service(db_session):
    cs = CustomerService()
    c = cs.create_customer("Juan", "0991234567", "Dir", "Ref")
    assert c.id is not None
    cs.update_customer(c.id, "Juan Mod", "0991234567", "Dir", "Ref")
    c_mod = cs.get_customer_by_id(c.id)
    assert c_mod.nombre == "Juan Mod"
    c_list = cs.get_all_customers()
    assert len(c_list) > 0

def test_product_service(db_session):
    ps = ProductService()
    p = ps.create_product("Coca Cola", ProductoTipo.bebida.value, "1.50", True, False)
    assert p.id is not None
    ps.update_product(p.id, "Coca Cola 1L", ProductoTipo.bebida.value, "1.75", True, False)
    p_mod = ps.get_product_by_id(p.id)
    assert p_mod.precio == Decimal("1.75")
    p_list = ps.get_all_products()
    assert len(p_list) > 0

def test_order_service(db_session):
    cs = CustomerService()
    c = cs.create_customer("Ana", "0991111111", "Dir", "Ref")
    
    ps = ProductService()
    p = ps.create_product("Pizza Vegana", ProductoTipo.pizza.value, "10.00", True, False)

    os = OrderService()
    pedido = os.create_order(c.id, CanalPedido.telefono.value, None, "Sin cebolla")
    assert pedido.id is not None
    assert pedido.estado == EstadoPedido.pendiente

    detalle = os.add_product_to_order(pedido.id, p.id, 2, "Extra queso", "Ok")
    assert detalle.id is not None
    
    pedido_updated = os.get_order_by_id(pedido.id)
    assert pedido_updated.total == Decimal("20.00")
    
    os.update_order_status(pedido.id, EstadoPedido.entregado.value)
    pedido_updated = os.get_order_by_id(pedido.id)
    assert pedido_updated.estado == EstadoPedido.entregado

def test_user_service(db_session):
    us = UserService()
    # It just needs to fetch users
    users = us.get_all_users()
    assert len(users) > 0
