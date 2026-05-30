from datetime import datetime, timezone
from uuid import uuid4

import crypto
import repository


QR_TYPE = "teacher_attendance_qr"


class QRValidationError(ValueError):
    pass


def create_teacher_qr_payload(teacher: dict, admin_id: str) -> tuple[str, dict]:
    token_id = str(uuid4())
    payload = {
        "v": 1,
        "typ": QR_TYPE,
        "token_id": token_id,
        "teacher_id": str(teacher["id"]),
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    encoded = crypto.encode_signed_envelope(payload)
    repository.create_qr_token({
        "token_id": token_id,
        "teacher_id": str(teacher["id"]),
        "payload": payload,
        "signature_hash": crypto.payload_hash({"encoded": encoded}),
        "issued_by_admin_id": admin_id,
        "revoked": False,
    })
    return encoded, payload


def validate_teacher_qr(encoded_payload: str) -> tuple[str, str]:
    try:
        payload = crypto.decode_signed_envelope(encoded_payload)
    except crypto.SignatureError as exc:
        raise QRValidationError(str(exc)) from exc

    if payload.get("typ") != QR_TYPE or payload.get("v") != 1:
        raise QRValidationError("QR payload is not a CITLog attendance token.")

    teacher_id = str(payload.get("teacher_id") or "").strip()
    token_id = str(payload.get("token_id") or "").strip()
    if not teacher_id or not token_id:
        raise QRValidationError("QR payload is missing required data.")

    token = repository.get_qr_token(token_id)
    if not token or str(token.get("teacher_id")) != teacher_id:
        raise QRValidationError("QR token is not registered or has been revoked.")

    teacher = repository.get_teacher(teacher_id)
    if not teacher:
        raise QRValidationError("QR token is not linked to an active teacher.")

    return teacher_id, token_id
