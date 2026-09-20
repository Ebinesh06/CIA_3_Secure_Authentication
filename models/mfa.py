from datetime import datetime

from . import db


class MFAConfiguration(db.Model):
    __tablename__ = "mfa_configurations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    secret = db.Column(db.String(64), nullable=False)
    enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")
