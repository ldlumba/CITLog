from datetime import datetime, timezone
from typing import Any

from postgrest.exceptions import APIError

from supabase_client import supabase


class RepositoryError(RuntimeError):
    pass


def _execute(query):
    try:
        return query.execute()
    except APIError as exc:
        raise RepositoryError(str(exc)) from exc


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_teacher(teacher_id: str) -> dict[str, Any] | None:
    response = _execute(
        supabase.table("teachers")
        .select("*")
        .eq("id", str(teacher_id))
        .eq("active", True)
        .limit(1)
    )
    return response.data[0] if response.data else None


def list_teachers() -> list[dict[str, Any]]:
    response = _execute(
        supabase.table("teachers")
        .select("*")
        .eq("active", True)
        .order("id")
    )
    return response.data or []


def create_teacher(teacher_id: str, first_name: str, last_name: str, created_by_admin_id: str) -> dict[str, Any]:
    response = _execute(
        supabase.table("teachers").insert({
            "id": str(teacher_id),
            "first_name": first_name,
            "last_name": last_name,
            "active": True,
            "created_by_admin_id": created_by_admin_id,
        })
    )
    return response.data[0]


def get_admin_by_username(username: str) -> dict[str, Any] | None:
    response = _execute(
        supabase.table("admin_users")
        .select("*")
        .eq("username", username.lower())
        .limit(1)
    )
    return response.data[0] if response.data else None


def get_admin_by_id(admin_id: str) -> dict[str, Any] | None:
    response = _execute(
        supabase.table("admin_users")
        .select("id, username, display_name, role, active")
        .eq("id", admin_id)
        .eq("active", True)
        .limit(1)
    )
    return response.data[0] if response.data else None


def update_admin_login_state(admin_id: str, values: dict[str, Any]) -> None:
    _execute(
        supabase.table("admin_users")
        .update(values)
        .eq("id", admin_id)
    )


def insert_attendance(record: dict[str, Any]) -> dict[str, Any]:
    response = _execute(supabase.table("attendance").insert(record))
    return response.data[0]


def list_attendance() -> list[dict[str, Any]]:
    response = _execute(
        supabase.table("attendance")
        .select("*")
        .order("id", desc=False)
    )
    return response.data or []


def latest_attendance_action(teacher_id: str) -> str | None:
    response = _execute(
        supabase.table("attendance")
        .select("id, action")
        .eq("teacher_id", str(teacher_id))
        .order("id", desc=True)
        .limit(1)
    )
    if not response.data:
        return None
    return str(response.data[0]["action"]).upper()


def create_qr_token(token: dict[str, Any]) -> dict[str, Any]:
    response = _execute(supabase.table("qr_tokens").insert(token))
    return response.data[0]


def get_qr_token(token_id: str) -> dict[str, Any] | None:
    response = _execute(
        supabase.table("qr_tokens")
        .select("*")
        .eq("token_id", token_id)
        .eq("revoked", False)
        .limit(1)
    )
    return response.data[0] if response.data else None


def clear_attendance() -> int:
    existing = _execute(supabase.table("attendance").select("id"))
    ids = [row["id"] for row in existing.data or []]
    if not ids:
        return 0
    _execute(supabase.table("attendance").delete().in_("id", ids))
    return len(ids)


def insert_audit_log(entry: dict[str, Any]) -> None:
    _execute(supabase.table("audit_logs").insert(entry))
