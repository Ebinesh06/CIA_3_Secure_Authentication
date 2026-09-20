from flask import Blueprint, render_template

from models import AuditLog, LoginAttempt
from utils.security import login_required

security_bp = Blueprint("security", __name__)


@security_bp.route("/security-logs")
@login_required
def security_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(25).all()
    attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(25).all()
    return render_template("security_logs.html", logs=logs, attempts=attempts)
