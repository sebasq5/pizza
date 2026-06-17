from sqlalchemy import select

from app.extensions import db
from app.models import Rol, RolNombre


class RolRepository:
    def list_all(self) -> list[Rol]:
        return list(db.session.scalars(select(Rol).order_by(Rol.nombre)))

    def get_by_name(self, role_name: RolNombre) -> Rol | None:
        return db.session.scalar(select(Rol).where(Rol.nombre == role_name))
