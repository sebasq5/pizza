from flask import jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.main import main_bp


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    metrics = {}
    if current_user.role_name == "administrador":
        from app.services.report_service import ReportService
        report_service = ReportService()
        metrics = report_service.get_dashboard_metrics()
        
    return render_template("main/dashboard.html", metrics=metrics)


@main_bp.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200
