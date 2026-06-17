import click
from flask import Flask

from app.services.seed_service import seed_roles_and_admin


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command():
        """Carga roles base y usuario administrador inicial."""
        created = seed_roles_and_admin()
        click.echo(created)
