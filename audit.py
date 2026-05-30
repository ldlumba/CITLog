from typing import Any

from flask import request, session

import repository


def log_audit(action: str, entity_type: str | None = None, entity_id: str | None = None, details: dict[str, Any] | None = None) -> None:
    actor = session.get("admin_user")
    entry = {
        "actor_admin_id": actor.get("id") if isinstance(actor, dict) else None,
        "actor_username": actor.get("username") if isinstance(actor, dict) else None,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details or {},
        "ip_address": request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip(),
        "user_agent": request.headers.get("User-Agent", "")[:500],
    }
    try:
        repository.insert_audit_log(entry)
    except Exception:
        pass
