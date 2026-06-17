from app.extensions import bcrypt
from app.repositories import UsuarioRepository


class AuthService:
    def __init__(self, user_repository: UsuarioRepository | None = None) -> None:
        self.user_repository = user_repository or UsuarioRepository()

    def authenticate(self, username: str, password: str):
        user = self.user_repository.get_by_username(username.strip())
        if not user or not user.activo:
            return None
        if not bcrypt.check_password_hash(user.password_hash, password):
            return None
        return user
