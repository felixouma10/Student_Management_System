import json

from models.user import User
from utils import storage


class AuthError(Exception):
    pass


def _session_file():
    return storage.DB_FILE.parent / "session.json"


def register(first_name, last_name, email, password, role="student"):
    if not User.all_users:
        role = "admin"
    elif role == "admin":
        raise AuthError("Administrator accounts can only be created by an administrator.")
    return User.register_user(first_name, last_name, email, password, role)


def login(email, password):
    user = User.find_user(email)
    if user is None or not user.check_password(password):
        raise AuthError("Invalid email or password.")
    try:
        _session_file().write_text(json.dumps({"email": user.email}), encoding="utf-8")
    except OSError as exc:
        raise AuthError(f"Could not start session: {exc}") from exc
    return user


def logout():
    try:
        _session_file().unlink()
    except FileNotFoundError:
        pass


def current_user():
    try:
        data = json.loads(_session_file().read_text(encoding="utf-8"))
        return User.find_user(data["email"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
