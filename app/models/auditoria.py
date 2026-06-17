from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.extensions import db

class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    accion = Column(String(100), nullable=False, index=True)
    tabla_afectada = Column(String(100), nullable=True)
    registro_id = Column(Integer, nullable=True)
    detalle = Column(Text, nullable=True)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    ip_origen = Column(String(50), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", backref="auditoria_registros")
