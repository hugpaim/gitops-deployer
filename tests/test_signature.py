# tests/test_signature.py
import hashlib
import hmac
from deployer.webhook.signature import verify_signature


def _make_sig(secret: str, payload: bytes) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_valid_signature():
    payload = b'{"ref": "refs/heads/main"}'
    secret = "mysecret"
    sig = _make_sig(secret, payload)
    assert verify_signature(payload, secret, sig) is True


def test_invalid_signature():
    payload = b'{"ref": "refs/heads/main"}'
    assert verify_signature(payload, "mysecret", "sha256=badhash") is False


def test_missing_signature():
    assert verify_signature(b"payload", "secret", "") is False


def test_wrong_prefix():
    assert verify_signature(b"payload", "secret", "md5=abc123") is False
