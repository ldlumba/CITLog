import pytest

import app as app_module
import routes.attendance as attendance_routes


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "log_audit", lambda *args, **kwargs: None)
    flask_app = app_module.create_app()
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return flask_app.test_client()


def test_manual_time_route_returns_signed_attendance(monkeypatch, client):
    teacher = {"id": "5035155459", "first_name": "Liandrei", "last_name": "Lumba"}

    monkeypatch.setattr(
        attendance_routes.attendance_service,
        "log_attendance",
        lambda teacher_id, action, source: ({"id": 1}, teacher, "signed-value"),
    )

    response = client.post("/time", json={"teacher_id": "5035155459", "action": "IN"})

    assert response.status_code == 200
    assert response.get_json()["signature"] == "signed-value"
    assert "Liandrei Lumba recorded for IN" in response.get_json()["message"]


def test_verify_route_requires_admin_session(client):
    response = client.get("/verify")

    assert response.status_code == 401


def test_verify_route_returns_rows_for_admin(monkeypatch, client):
    monkeypatch.setattr(
        attendance_routes.attendance_service,
        "verified_attendance_rows",
        lambda: [{"id": 1, "teacher_id": "T1", "valid": True}],
    )
    monkeypatch.setattr(attendance_routes, "log_audit", lambda *args, **kwargs: None)

    with client.session_transaction() as session:
        session["admin_user"] = {"id": "admin-id", "username": "admin", "role": "admin"}

    response = client.get("/verify")

    assert response.status_code == 200
    assert response.get_json()[0]["valid"] is True


def test_admin_login_route_sets_session(monkeypatch, client):
    monkeypatch.setattr(
        app_module,
        "login_admin",
        lambda username, password: {"id": "admin-id", "username": username, "role": "admin"},
    )

    response = client.post("/admin/login", json={"username": "admin", "password": "secret"})

    assert response.status_code == 200
    assert response.get_json()["admin"]["role"] == "admin"
