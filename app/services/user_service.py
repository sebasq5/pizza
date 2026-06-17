from sqlalchemy.exc import IntegrityError

from app.extensions import bcrypt, db
from app.models import RolNombre, Usuario
from app.repositories import RolRepository, UsuarioRepository


class UserService:
    def __init__(
        self,
        user_repository: UsuarioRepository | None = None,
        role_repository: RolRepository | None = None,
    ) -> None:
        self.user_repository = user_repository or UsuarioRepository()
        self.role_repository = role_repository or RolRepository()

    def list_users(self) -> list[Usuario]:
        return self.user_repository.list_all()

    def list_roles(self):
        return self.role_repository.list_all()

    def get_user(self, user_id: int) -> Usuario | None:
        return self.user_repository.get(user_id)

    def create_user(
        self,
        full_name: str,
        username: str,
        password: str,
        role_name: str,
        active: bool,
    ) -> Usuario:
        role = self.role_repository.get_by_name(RolNombre(role_name))
        if role is None:
            raise ValueError("Rol inválido.")
        if self.user_repository.get_by_username(username.strip()):
            raise ValueError("El nombre de usuario ya existe.")

        user = Usuario(
            nombre=full_name.strip(),
            usuario=username.strip(),
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            rol=role,
            activo=active,
        )
        try:
            return self.user_repository.add(user)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo crear el usuario.") from exc

    def update_user(
        self,
        user: Usuario,
        full_name: str,
        username: str,
        role_name: str,
        active: bool,
        password: str | None = None,
    ) -> Usuario:
        role = self.role_repository.get_by_name(RolNombre(role_name))
        if role is None:
            raise ValueError("Rol inválido.")

        existing = self.user_repository.get_by_username(username.strip())
        if existing and existing.id != user.id:
            raise ValueError("El nombre de usuario ya existe.")

        user.nombre = full_name.strip()
        user.usuario = username.strip()
        user.rol = role
        user.activo = active
        if password:
            user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            self.user_repository.save()
            return user
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo actualizar el usuario.") from exc

    def delete_user(self, user: Usuario, current_user_id: int) -> None:
        if user.id == current_user_id:
            raise ValueError("No puedes eliminar tu propia cuenta activa.")
        try:
            self.user_repository.delete(user)
        except IntegrityError as exc:
            db.session.rollback()
            raise ValueError("No se pudo eliminar el usuario.") from exc
