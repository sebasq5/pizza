from app.repositories.cliente_repository import ClienteRepository
from app.repositories.detalle_pedido_repository import DetallePedidoRepository
from app.repositories.pedido_repository import PedidoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.role_repository import RolRepository
from app.repositories.user_repository import UsuarioRepository
from app.repositories.venta_repository import VentaRepository

__all__ = [
    "ClienteRepository",
    "DetallePedidoRepository",
    "PedidoRepository",
    "ProductoRepository",
    "RolRepository",
    "UsuarioRepository",
    "VentaRepository",
]
