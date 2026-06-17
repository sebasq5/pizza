import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.extensions import db

class EstadoCaja(enum.Enum):
    abierta = "abierta"
    cerrada = "cerrada"

class Caja(db.Model):
    __tablename__ = "cajas"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha_apertura = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    monto_apertura = Column(Numeric(10, 2), nullable=False)
    
    fecha_cierre = Column(DateTime, nullable=True)
    monto_esperado = Column(Numeric(10, 2), nullable=True)
    monto_real = Column(Numeric(10, 2), nullable=True)
    diferencia = Column(Numeric(10, 2), nullable=True)
    
    estado = Column(Enum(EstadoCaja, name="estado_caja_enum"), default=EstadoCaja.abierta, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", backref="cajas")
