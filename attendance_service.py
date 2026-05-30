from datetime import datetime
from zoneinfo import ZoneInfo

from config import settings
import crypto
import repository


class AttendanceError(ValueError):
    pass


def teacher_display_name(teacher: dict) -> str:
    return f"{teacher['first_name']} {teacher['last_name']}"


def normalize_teacher_id(teacher_id: str) -> str:
    normalized = str(teacher_id or "").strip()
    if not normalized or len(normalized) > 64:
        raise AttendanceError("Invalid Teacher ID.")
    return normalized


def normalize_action(action: str) -> str:
    normalized = str(action or "").strip().upper()
    if normalized not in {"IN", "OUT"}:
        raise AttendanceError("Invalid attendance action.")
    return normalized


def build_record(teacher_id: str, action: str) -> dict[str, str]:
    now = datetime.now(ZoneInfo(settings.app_timezone))
    return {
        "teacher_id": teacher_id,
        "date": str(now.date()),
        "time": now.strftime("%H:%M:%S"),
        "action": action,
    }


def next_scan_action(teacher_id: str) -> str:
    return "OUT" if repository.latest_attendance_action(teacher_id) == "IN" else "IN"


def log_attendance(teacher_id: str, action: str, source: str, qr_token_id: str | None = None) -> tuple[dict, dict, str]:
    normalized_teacher_id = normalize_teacher_id(teacher_id)
    normalized_action = normalize_action(action)
    teacher = repository.get_teacher(normalized_teacher_id)
    if not teacher:
        raise AttendanceError("Invalid Teacher ID.")

    record = build_record(normalized_teacher_id, normalized_action)
    payload = crypto.attendance_payload(record)
    signature = crypto.sign_payload(payload)
    inserted = repository.insert_attendance({
        **record,
        "payload_hash": crypto.payload_hash(payload),
        "signature": signature,
        "signing_key_id": settings.signing_key_id,
        "qr_token_id": qr_token_id,
        "source": source,
    })
    return inserted, teacher, signature


def verify_attendance_entry(entry: dict) -> bool:
    payload = crypto.attendance_payload(entry)
    signature = entry.get("signature")
    if not isinstance(signature, str) or not signature:
        return False
    if entry.get("payload_hash") != crypto.payload_hash(payload):
        return False
    return crypto.verify_payload(payload, signature)


def verified_attendance_rows() -> list[dict]:
    rows = []
    teacher_cache: dict[str, str] = {}
    for entry in repository.list_attendance():
        teacher_id = str(entry.get("teacher_id"))
        if teacher_id not in teacher_cache:
            teacher = repository.get_teacher(teacher_id)
            teacher_cache[teacher_id] = teacher_display_name(teacher) if teacher else "Unknown"
        rows.append({
            "id": entry["id"],
            "teacher_id": teacher_id,
            "name": teacher_cache[teacher_id],
            "date": str(entry["date"]),
            "time": str(entry["time"]),
            "action": str(entry["action"]),
            "valid": verify_attendance_entry(entry),
        })
    return rows
