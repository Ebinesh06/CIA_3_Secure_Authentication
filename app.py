from flask import Flask, redirect, session, url_for
from flask_talisman import Talisman
from dotenv import load_dotenv
import pyotp

from ai.risk_engine import train_model_if_needed
from config import Config
from models import MFAConfiguration, User, db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.security import security_bp
from utils.security import hash_password, limiter

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
limiter.init_app(app)

Talisman(
    app,
    content_security_policy={
        "default-src": "'self'",
        "img-src": "'self' data: https:",
        "script-src": "'self' 'unsafe-inline'",
        "style-src": "'self' 'unsafe-inline'",
        "connect-src": "'self'",
    },
    force_https=False,
    frame_options={"action": "DENY"},
    strict_transport_security=False,
)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(security_bp)


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard_home"))
    return redirect(url_for("auth.login"))


@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
        train_model_if_needed(force=True)

        demo_user = User.query.filter_by(username="demo").first()
        if not demo_user:
            demo_user = User(
                username="demo",
                email="demo@example.com",
                password_hash=hash_password("Demo@123"),
                mfa_secret=pyotp.random_base32(),
            )
            db.session.add(demo_user)
            db.session.commit()

            demo_mfa = MFAConfiguration(user_id=demo_user.id, secret=demo_user.mfa_secret, enabled=False)
            db.session.add(demo_mfa)
            db.session.commit()

        print("Database initialized and demo account created.")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
