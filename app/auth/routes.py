from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.services import AuthService


def _is_safe_redirect_target(target: str | None) -> bool:
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        auth_service = AuthService()
        user = auth_service.authenticate(form.username.data, form.password.data)
        if user is None:
            flash("Credenciales inválidas o usuario inactivo.", "danger")
            return render_template("auth/login.html", form=form), 401

        login_user(user, remember=form.remember_me.data)
        next_url = request.args.get("next")
        flash("Sesión iniciada correctamente.", "success")
        if _is_safe_redirect_target(next_url):
            return redirect(next_url)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
