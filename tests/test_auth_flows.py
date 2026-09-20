import pyotp
import pytest

from app import app
from models import AuditLog, MFAConfiguration, User, db
from utils.security import hash_password, verify_password


@pytest.fixture()
def client():
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI="sqlite://",
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def create_demo_user():
    user = User(
        username="demo",
        email="demo@example.com",
        password_hash=hash_password("Demo@123"),
        mfa_secret=pyotp.random_base32(),
    )
    db.session.add(user)
    db.session.commit()

    mfa_cfg = MFAConfiguration(user_id=user.id, secret=user.mfa_secret, enabled=False)
    db.session.add(mfa_cfg)
    db.session.commit()
    return user


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"AI Risk-Adaptive Secure Authentication" in response.data


def test_password_hash_and_verify():
    hashed = hash_password("Demo@123")
    assert hashed != "Demo@123"
    assert verify_password("Demo@123", hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_normal_login_flow(client):
    create_demo_user()

    response = client.post(
        "/login",
        data={"username": "demo", "password": "Demo@123", "demo_mode": "normal"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Authentication Dashboard" in response.data
    assert b"Welcome, demo" in response.data


def test_medium_risk_login_requires_mfa_and_succeeds(client):
    user = create_demo_user()

    response = client.post(
        "/login",
        data={"username": "demo", "password": "Demo@123", "demo_mode": "medium"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers.get("Location") == "/mfa"

    otp = pyotp.TOTP(user.mfa_secret).now()
    response = client.post("/mfa", data={"otp": otp}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Authentication Dashboard" in response.data
    with client.session_transaction() as session:
        assert session.get("user_id") == user.id


def test_high_risk_login_is_blocked(client):
    create_demo_user()

    response = client.post(
        "/login",
        data={"username": "demo", "password": "Demo@123", "demo_mode": "high"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "HIGH" in page or "blocked" in page.lower()


def test_audit_log_records_security_events(client):
    create_demo_user()

    client.post(
        "/login",
        data={"username": "demo", "password": "Demo@123", "demo_mode": "medium"},
        follow_redirects=False,
    )

    otp = pyotp.TOTP(User.query.first().mfa_secret).now()
    client.post("/mfa", data={"otp": otp}, follow_redirects=False)

    assert AuditLog.query.filter_by(event="mfa_required").count() >= 1
    assert AuditLog.query.filter_by(event="mfa_success").count() >= 1
    assert AuditLog.query.count() >= 2
