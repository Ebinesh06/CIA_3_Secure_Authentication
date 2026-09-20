import re
from typing import Optional


def validate_username(username: str) -> Optional[str]:
    if not username or len(username.strip()) < 3:
        return "Username must contain at least 3 characters."
    if len(username) > 30:
        return "Username must be shorter than 30 characters."
    if not re.match(r"^[A-Za-z0-9_@.-]+$", username):
        return "Username may contain only letters, numbers, underscore, dot, dash, and @."
    return None


def validate_email(email: str) -> Optional[str]:
    if not email or "@" not in email:
        return "Please enter a valid email address."
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(pattern, email):
        return "Please enter a valid email address."
    return None


def validate_password(password: str) -> Optional[str]:
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."
    return None
