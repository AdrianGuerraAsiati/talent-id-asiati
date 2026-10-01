import hashlib
import hmac
import secrets


def issue_device_secret() -> str:
    return secrets.token_urlsafe(32)


def hash_device_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def verify_device_secret(secret: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_device_secret(secret), expected_hash)
