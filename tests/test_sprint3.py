import pytest
from decimal import Decimal
from app.models import EstadoVenta, MetodoPago, MotivoMovimiento, TipoMovimiento
from app.services.inventory_service import InventoryService
from app.services.payment_service import PaymentService
from app.models.ingrediente import Ingrediente, UnidadMedida

def test_inventory_service_deduction(app, db, test_user):
    # Setup test logic later
    pass

def test_payment_service(app, db, test_user):
    # Setup test logic later
    pass
