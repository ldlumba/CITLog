import base64
import json
from hashlib import sha256
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from config import settings


class SignatureError(ValueError):
    pass


def _urlsafe_b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def payload_hash(payload: dict[str, Any]) -> str:
    return sha256(canonical_json(payload)).hexdigest()


def load_private_key(raw_key_b64: str | None = None) -> Ed25519PrivateKey:
    raw_key = base64.b64decode(raw_key_b64 or settings.signing_private_key_b64)
    if len(raw_key) == 32:
        return Ed25519PrivateKey.from_private_bytes(raw_key)
    return serialization.load_pem_private_key(raw_key, password=None)


def public_key_b64(private_key: Ed25519PrivateKey | None = None) -> str:
    key = private_key or load_private_key()
    raw_public = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw_public).decode("ascii")


def sign_payload(payload: dict[str, Any], private_key: Ed25519PrivateKey | None = None) -> str:
    key = private_key or load_private_key()
    return _urlsafe_b64encode(key.sign(canonical_json(payload)))


def verify_payload(payload: dict[str, Any], signature: str, public_key_b64_value: str | None = None) -> bool:
    try:
        if public_key_b64_value:
            raw_public = base64.b64decode(public_key_b64_value)
            public_key = Ed25519PublicKey.from_public_bytes(raw_public)
        else:
            public_key = load_private_key().public_key()
        public_key.verify(_urlsafe_b64decode(signature), canonical_json(payload))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def encode_signed_envelope(payload: dict[str, Any]) -> str:
    envelope = {
        "payload": payload,
        "signature": sign_payload(payload),
        "key_id": settings.signing_key_id,
    }
    return "CITLOG1." + _urlsafe_b64encode(canonical_json(envelope))


def decode_signed_envelope(encoded: str) -> dict[str, Any]:
    if not encoded.startswith("CITLOG1."):
        raise SignatureError("Unsupported QR payload format.")
    try:
        envelope = json.loads(_urlsafe_b64decode(encoded.split(".", 1)[1]).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise SignatureError("Malformed QR payload.") from exc

    payload = envelope.get("payload")
    signature = envelope.get("signature")
    key_id = envelope.get("key_id")
    if not isinstance(payload, dict) or not isinstance(signature, str) or key_id != settings.signing_key_id:
        raise SignatureError("Invalid QR payload envelope.")
    if not verify_payload(payload, signature):
        raise SignatureError("QR payload signature is invalid.")
    return payload


def attendance_payload(record: dict[str, Any]) -> dict[str, str]:
    return {
        "teacher_id": str(record["teacher_id"]),
        "date": str(record["date"]),
        "time": str(record["time"]),
        "action": str(record["action"]).upper(),
    }
