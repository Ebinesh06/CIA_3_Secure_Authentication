from datetime import datetime

from . import db


class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(250), nullable=True)
    failed = db.Column(db.Boolean, default=False)
    risk_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(20), nullable=True)
    outcome = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)

    user = db.relationship("User")
