import base64
import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


private_key = Ed25519PrivateKey.generate()
private_raw = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
)

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("CITLOG_SIGNING_PRIVATE_KEY_B64", base64.b64encode(private_raw).decode("ascii"))
os.environ.setdefault("CITLOG_SIGNING_KEY_ID", "test-key")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
