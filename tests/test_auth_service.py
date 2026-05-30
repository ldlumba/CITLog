import pytest
from flask import Flask
from werkzeug.security import generate_password_hash

import auth_service


def test_login_admin_sets_role_session(monkeypatch):
    admin = {
        "id": "admin-id",
        "username": "admin",
        "display_name": "Admin User",
        "role": "admin",
        "active": True,
        "password_hash": generate_password_hash("correct-password", method="scrypt"),
        "failed_login_count": 0,
        "locked_until": None,
    }
    updates = []

    monkeypatch.setattr(auth_service.repository, "get_admin_by_username", lambda username: admin)
    monkeypatch.setattr(auth_service.repository, "update_admin_login_state", lambda admin_id, values: updates.append((admin_id, values)))

    app = Flask(__name__)
    app.secret_key = "test-secret"
    with app.test_request_context("/admin/login", method="POST"):
        logged_in = auth_service.login_admin("admin", "correct-password")

    assert logged_in["id"] == "admin-id"
    assert logged_in["role"] == "admin"
    assert updates[-1][1]["failed_login_count"] == 0


def test_permissions_for_admin_role():
    permissions = auth_service.permissions_for("admin")

    assert "view_attendance" in permissions
    assert "manage_teachers" in permissions
    assert "clear_attendance" in permissions


def test_invalid_username_rejected():
    with pytest.raises(auth_service.AuthError):
        auth_service.normalize_username("../admin")
