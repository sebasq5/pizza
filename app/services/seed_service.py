from flask import current_app

from app.extensions import db
from app.models import Rol, RolNombre, Usuario
from app.repositories import RolRepository, UsuarioRepository
from app.services.user_service import UserService


def seed_roles_and_admin() -> str:
    role_repository = RolRepository()
    user_repository = UsuarioRepository()
    user_service = UserService(user_repository=user_repository, role_repository=role_repository)

    created_roles = 0
    for role_name in RolNombre:
        if role_repository.get_by_name(role_name) is None:
            db.session.add(
                Rol(
                    nombre=role_name,
                    descripcion=f"Rol base: {role_name.value}",
                )
            )
            created_roles += 1

    if created_roles:
        db.session.commit()

    admin_username = current_app.config["ADMIN_USERNAME"]
    if user_repository.get_by_username(admin_username) is None:
        user_service.create_user(
            full_name=current_app.config["ADMIN_FULL_NAME"],
            username=admin_username,
            password=current_app.config["ADMIN_PASSWORD"],
            role_name=RolNombre.administrador.value,
            active=True,
        )
        return "Seed ejecutado: roles base creados y administrador inicial generado."

    return "Seed ejecutado: roles verificados y administrador ya existente."
