import hashlib
import hmac
import secrets

ITERATIONS = 100_000


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    try:
        salt, _ = stored.split("$")
        return hmac.compare_digest(hash_password(password, salt), stored)
    except (ValueError, AttributeError):
        return False
