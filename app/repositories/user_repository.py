from sqlalchemy import select

from app.extensions import db
from app.models import RolNombre, Usuario


class UsuarioRepository:
    def list_all(self) -> list[Usuario]:
        return list(
            db.session.scalars(select(Usuario).order_by(Usuario.fecha_creacion.desc()))
        )

    def get(self, user_id: int) -> Usuario | None:
        return db.session.get(Usuario, user_id)

    def get_by_username(self, username: str) -> Usuario | None:
        return db.session.scalar(select(Usuario).where(Usuario.usuario == username))

    def add(self, user: Usuario) -> Usuario:
        db.session.add(user)
        db.session.commit()
        return user

    def list_active_by_role(self, role_name: RolNombre) -> list[Usuario]:
        query = (
            select(Usuario)
            .join(Usuario.rol)
            .where(Usuario.activo.is_(True), Usuario.rol.has(nombre=role_name))
            .order_by(Usuario.nombre.asc())
        )
        return list(db.session.scalars(query))

    def save(self) -> None:
        db.session.commit()

    def delete(self, user: Usuario) -> None:
        db.session.delete(user)
        db.session.commit()
