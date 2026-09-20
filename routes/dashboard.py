from flask import Blueprint, flash, render_template, request
import pyotp

from models import AuditLog, LoginAttempt, MFAConfiguration, db
from utils.security import get_current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_home():
    user = get_current_user()
    total_attempts = LoginAttempt.query.count()
    successful_logins = LoginAttempt.query.filter_by(outcome="success").count()
    failed_logins = LoginAttempt.query.filter_by(failed=True).count()
    suspicious_logins = LoginAttempt.query.filter(LoginAttempt.risk_level == "MEDIUM").count()
    blocked_logins = LoginAttempt.query.filter(LoginAttempt.outcome == "blocked").count()
    mfa_challenges = AuditLog.query.filter_by(event="mfa_required").count()
    recent_events = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    recent_attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(10).all()

    risk_scores = [attempt.risk_score for attempt in recent_attempts if attempt.risk_score is not None]
    login_activity = []
    for entry in reversed(recent_attempts):
        login_activity.append({
            "label": entry.timestamp.strftime("%H:%M") if entry.timestamp else "now",
            "value": 1 if entry.outcome in ["success", "evaluated"] else 0,
        })

    return render_template(
        "dashboard.html",
        user=user,
        total_attempts=total_attempts,
        successful_logins=successful_logins,
        failed_logins=failed_logins,
        suspicious_logins=suspicious_logins,
        blocked_logins=blocked_logins,
        mfa_challenges=mfa_challenges,
        recent_events=recent_events,
        risk_scores=risk_scores,
        login_activity=login_activity,
        recent_attempts=recent_attempts,
    )


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    mfa_cfg = MFAConfiguration.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
        if not mfa_cfg:
            mfa_cfg = MFAConfiguration(user_id=user.id, secret=user.mfa_secret, enabled=False)
            db.session.add(mfa_cfg)

        otp = (request.form.get("otp") or "").strip()
        if otp:
            if pyotp.TOTP(user.mfa_secret).verify(otp, valid_window=1):
                mfa_cfg.enabled = True
                db.session.commit()
                flash("MFA enabled successfully.", "success")
            else:
                flash("MFA verification failed.", "danger")
        else:
            flash("MFA setup has been prepared. Enter the OTP to enable it.", "info")

    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        db.session.commit()

    if not mfa_cfg:
        mfa_cfg = MFAConfiguration(user_id=user.id, secret=user.mfa_secret, enabled=False)
        db.session.add(mfa_cfg)
        db.session.commit()

    return render_template("profile.html", user=user, secret=user.mfa_secret, mfa_enabled=mfa_cfg.enabled)
