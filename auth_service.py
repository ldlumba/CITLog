from datetime import datetime, timedelta, timezone
from functools import wraps
import re
from typing import Callable

from flask import jsonify, redirect, session, url_for
from werkzeug.security import check_password_hash

from config import settings
import repository


ROLE_PERMISSIONS = {
    "viewer": {"view_dashboard", "view_attendance", "list_teachers"},
    "admin": {"view_dashboard", "view_attendance", "list_teachers", "manage_teachers", "generate_qr", "clear_attendance"},
    "super_admin": {"view_dashboard", "view_attendance", "list_teachers", "manage_teachers", "generate_qr", "clear_attendance", "manage_admins"},
}


USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.@-]{3,120}$")


class AuthError(ValueError):
    pass


def normalize_username(username: str) -> str:
    normalized = str(username or "").strip().lower()
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise AuthError("Invalid username or password.")
    return normalized


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def permissions_for(role: str) -> set[str]:
    return ROLE_PERMISSIONS.get(role, set())


def current_admin() -> dict | None:
    user = session.get("admin_user")
    if not isinstance(user, dict) or not user.get("id"):
        return None
    return user


def has_permission(permission: str) -> bool:
    user = current_admin()
    if not user:
        return False
    return permission in permissions_for(str(user.get("role", "")))


def login_admin(username: str, password: str) -> dict:
    normalized = normalize_username(username)
    admin = repository.get_admin_by_username(normalized)
    now = datetime.now(timezone.utc)

    if not admin or not admin.get("active"):
        raise AuthError("Invalid username or password.")

    locked_until = parse_datetime(admin.get("locked_until"))
    if locked_until and locked_until > now:
        remaining = max(1, int((locked_until - now).total_seconds()))
        raise AuthError(f"Too many failed attempts. Try again in {remaining} seconds.")

    password_hash = admin.get("password_hash") or ""
    if not check_password_hash(password_hash, str(password or "")):
        failed_count = int(admin.get("failed_login_count") or 0) + 1
        values = {"failed_login_count": failed_count}
        if failed_count >= settings.max_login_attempts:
            values["locked_until"] = (now + timedelta(seconds=settings.login_cooldown_seconds)).isoformat()
        repository.update_admin_login_state(admin["id"], values)
        raise AuthError("Invalid username or password.")

    repository.update_admin_login_state(
        admin["id"],
        {
            "failed_login_count": 0,
            "locked_until": None,
            "last_login_at": now.isoformat(),
        },
    )
    session.permanent = True
    session["admin_user"] = {
        "id": admin["id"],
        "username": admin["username"],
        "display_name": admin.get("display_name") or admin["username"],
        "role": admin["role"],
    }
    return session["admin_user"]


def logout_admin() -> None:
    session.pop("admin_user", None)


def admin_required(permission: str = "view_dashboard"):
    def decorator(view: Callable):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_admin():
                return jsonify({"error": "Unauthorized"}), 401
            if not has_permission(permission):
                return jsonify({"error": "Forbidden"}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator


def page_admin_required(view: Callable):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_admin():
            return redirect(url_for("home"))
        if not has_permission("view_dashboard"):
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped
