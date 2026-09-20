from datetime import datetime

from . import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event = db.Column(db.String(80), nullable=False)
    risk_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(20), nullable=True)
    action = db.Column(db.String(80), nullable=True)
    details = db.Column(db.Text, nullable=True)

    user = db.relationship("User")
