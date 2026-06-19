from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.services import AuthService
from app.services.audit_service import AuditService


def _is_safe_redirect_target(target: str | None) -> bool:
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


from app.extensions import limiter

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        auth_service = AuthService()
        user = auth_service.authenticate(form.username.data, form.password.data)
        if user is None:
            flash("Credenciales inválidas o usuario inactivo.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        
        audit_service = AuditService()
        audit_service.log_action(
            usuario_id=user.id,
            accion="login",
            detalle="Inicio de sesión exitoso"
        )
        
        next_url = request.args.get("next")
        flash("Sesión iniciada correctamente.", "success")
        if _is_safe_redirect_target(next_url):
            return redirect(next_url)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    audit_service = AuditService()
    audit_service.log_action(
        usuario_id=current_user.id,
        accion="logout",
        detalle="Cierre de sesión"
    )
    
    logout_user()
    from flask import session
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
