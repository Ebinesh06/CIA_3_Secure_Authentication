from datetime import datetime, timedelta

import pyotp
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ai.risk_engine import assess_login_risk
from config import Config
from models import AuditLog, LoginAttempt, MFAConfiguration, User, db
from utils.security import (
    create_access_token,
    get_client_ip,
    hash_password,
    limiter,
    login_required,
    verify_password,
)
from utils.validation import validate_email, validate_password, validate_username

auth_bp = Blueprint("auth", __name__)


def _get_login_features(user: User, ip_address: str, user_agent: str, demo_mode: str = "normal"):
    current_hour = datetime.utcnow().hour
    recent_attempts = (
        LoginAttempt.query.filter(
            LoginAttempt.user_id == user.id,
            LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24),
        ).count()
        if user
        else 0
    )
    last_login = user.last_login_at if user else None
    time_since_previous_login = 0
    if last_login:
        delta = datetime.utcnow() - last_login
        time_since_previous_login = max(0.0, delta.total_seconds() / 60.0)

    is_first_login = bool(user and not user.last_login_at and not user.last_ip and not user.last_device)
    features = {
        "login_hour": float(current_hour),
        "failed_attempts": int(user.failed_attempts if user else 0),
        "recent_attempts": int(recent_attempts),
        "new_ip": 0 if is_first_login else (1 if user and (not user.last_ip or user.last_ip != ip_address) else 0),
        "new_device": 0 if is_first_login else (1 if user and (not user.last_device or user.last_device != user_agent) else 0),
        "time_since_previous_login": float(time_since_previous_login),
        "login_frequency": 1 + recent_attempts,
    }

    if demo_mode == "medium":
        features.update(
            {
                "login_hour": 10.0,
                "failed_attempts": 1,
                "recent_attempts": 3,
                "new_ip": 1,
                "new_device": 1,
                "time_since_previous_login": 90.0,
                "login_frequency": 4,
            }
        )
    elif demo_mode == "high":
        features.update(
            {
                "login_hour": 3.0,
                "failed_attempts": 6,
                "recent_attempts": 9,
                "new_ip": 1,
                "new_device": 1,
                "time_since_previous_login": 300.0,
                "login_frequency": 12,
            }
        )

    return features


def _record_audit(user: User | None, event: str, risk_score: int | None, risk_level: str | None, action: str, details: str):
    log_entry = AuditLog(
        user_id=user.id if user else None,
        event=event,
        risk_score=risk_score,
        risk_level=risk_level,
        action=action,
        details=details,
    )
    db.session.add(log_entry)
    db.session.commit()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        username_error = validate_username(username)
        if username_error:
            flash(username_error, "danger")
            return render_template("register.html")

        email_error = validate_email(email)
        if email_error:
            flash(email_error, "danger")
            return render_template("register.html")

        password_error = validate_password(password)
        if password_error:
            flash(password_error, "danger")
            return render_template("register.html")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("An account with that username or email already exists.", "warning")
            return render_template("register.html")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            mfa_secret=pyotp.random_base32(),
        )
        db.session.add(user)
        db.session.commit()

        mfa_cfg = MFAConfiguration(user_id=user.id, secret=user.mfa_secret, enabled=False)
        db.session.add(mfa_cfg)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("6 per minute")
def login():
    if request.method == "POST":
        username_or_email = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        demo_mode = request.form.get("demo_mode", "normal")

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()

        if user and user.locked_until and user.locked_until > datetime.utcnow():
            flash("Account temporarily locked due to repeated failed attempts. Please try again later.", "warning")
            _record_audit(user, "login_blocked", None, "LOCKED", "blocked", "Repeated failed attempts triggered lockout")
            return render_template("login.html", risk_status="HIGH", risk_result={"risk_score": 85, "risk_level": "HIGH", "reasons": ["Temporary lockout due to repeated failed attempts"], "recommendation": "Block login until lockout expires"})

        if not user or not verify_password(password, user.password_hash):
            if user:
                user.failed_attempts += 1
                if user.failed_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=Config.LOCKOUT_MINUTES)
                db.session.commit()
            ip_address = get_client_ip()
            user_agent = request.headers.get("User-Agent", "unknown")
            _record_audit(
                user,
                "login_failed",
                0,
                "LOW",
                "failed",
                "Generic authentication failure recorded",
            )
            db.session.add(
                LoginAttempt(
                    user_id=user.id if user else None,
                    timestamp=datetime.utcnow(),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failed=True,
                    risk_score=0,
                    risk_level="LOW",
                    outcome="failed",
                    details="Invalid credentials or generic failure",
                )
            )
            db.session.commit()
            flash("Login failed. Please check your credentials and try again.", "danger")
            return render_template("login.html", risk_status="LOW")

        user.failed_attempts = 0
        user.locked_until = None
        user.last_ip = get_client_ip()
        user.last_device = request.headers.get("User-Agent", "unknown")
        db.session.commit()

        ip_address = get_client_ip()
        user_agent = request.headers.get("User-Agent", "unknown")
        features = _get_login_features(user, ip_address, user_agent, demo_mode)
        risk_result = assess_login_risk(features)

        login_record = LoginAttempt(
            user_id=user.id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            failed=False,
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            outcome="evaluated",
            details=", ".join(risk_result["reasons"]),
        )
        db.session.add(login_record)
        db.session.commit()

        if risk_result["risk_level"] == "HIGH":
            login_record.outcome = "blocked"
            login_record.failed = True
            db.session.commit()
            flash("This login attempt was blocked because it was classified as high-risk.", "danger")
            user.failed_attempts = min(user.failed_attempts + 1, 10)
            db.session.commit()
            _record_audit(user, "login_blocked", risk_result["risk_score"], risk_result["risk_level"], "blocked", ", ".join(risk_result["reasons"]))
            return render_template(
                "login.html",
                risk_status="HIGH",
                risk_result=risk_result,
                blocked=True,
            )

        if risk_result["risk_level"] == "MEDIUM":
            login_record.outcome = "mfa_required"
            db.session.commit()
            session["pending_mfa_user_id"] = user.id
            session["pending_risk_result"] = risk_result
            flash("Medium-risk login detected. MFA verification is required.", "warning")
            _record_audit(user, "mfa_required", risk_result["risk_score"], risk_result["risk_level"], "mfa", ", ".join(risk_result["reasons"]))
            return redirect(url_for("auth.mfa"))

        login_record.outcome = "success"
        db.session.commit()
        token = create_access_token(user)
        session["user_id"] = user.id
        session["access_token"] = token
        user.last_login_at = datetime.utcnow()
        user.last_ip = ip_address
        user.last_device = user_agent
        db.session.commit()
        _record_audit(user, "login_success", risk_result["risk_score"], risk_result["risk_level"], "allow", ", ".join(risk_result["reasons"]))
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template("login.html", risk_status="LOW")


@auth_bp.route("/mfa", methods=["GET", "POST"])
def mfa():
    pending_user_id = session.get("pending_mfa_user_id")
    if not pending_user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(pending_user_id)
    if not user:
        return redirect(url_for("auth.login"))

    risk_result = session.get("pending_risk_result", {"risk_score": 50, "risk_level": "MEDIUM", "reasons": ["Unusual login behavior detected"], "recommendation": "Require MFA"})
    mfa_config = MFAConfiguration.query.filter_by(user_id=user.id).first()
    if not mfa_config:
        secret = pyotp.random_base32()
        mfa_config = MFAConfiguration(user_id=user.id, secret=secret, enabled=False)
        db.session.add(mfa_config)
        db.session.commit()
    else:
        secret = mfa_config.secret

    if request.method == "POST":
        otp = (request.form.get("otp") or "").strip()
        totp = pyotp.TOTP(secret)
        if totp.verify(otp, valid_window=1):
            mfa_config.enabled = True
            db.session.commit()
            session.pop("pending_mfa_user_id", None)
            session.pop("pending_risk_result", None)

            latest_attempt = LoginAttempt.query.filter_by(user_id=user.id).order_by(LoginAttempt.timestamp.desc()).first()
            if latest_attempt:
                latest_attempt.outcome = "success"
                latest_attempt.failed = False
                latest_attempt.risk_score = risk_result.get("risk_score")
                latest_attempt.risk_level = risk_result.get("risk_level")
                latest_attempt.details = ", ".join(risk_result.get("reasons", []))

            token = create_access_token(user)
            session["user_id"] = user.id
            session["access_token"] = token
            user.last_login_at = datetime.utcnow()
            user.last_ip = get_client_ip()
            user.last_device = request.headers.get("User-Agent", "unknown")
            user.failed_attempts = 0
            user.locked_until = None
            db.session.commit()
            _record_audit(user, "mfa_success", risk_result["risk_score"], risk_result["risk_level"], "allow", "MFA passed")
            flash("MFA verified. Login successful.", "success")
            return redirect(url_for("dashboard.dashboard_home"))

        flash("MFA verification failed. Please try again.", "danger")
        _record_audit(user, "mfa_failed", risk_result["risk_score"], risk_result["risk_level"], "failed", "OTP verification failed")
        return render_template("mfa.html", user=user, secret=secret, risk_result=risk_result)

    return render_template("mfa.html", user=user, secret=secret, risk_result=risk_result)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
