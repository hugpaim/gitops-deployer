# deployer/webhook/signature.py
import hashlib
import hmac


def verify_signature(payload: bytes, secret: str, signature_header: str) -> bool:
    """Validate GitHub's X-Hub-Signature-256 header."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    received = signature_header[len("sha256="):]
    return hmac.compare_digest(expected, received)
