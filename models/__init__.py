from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .audit_log import AuditLog
from .login_attempt import LoginAttempt
from .mfa import MFAConfiguration
from .user import User
