import pytest

import qr_service


def test_create_and_validate_teacher_qr(monkeypatch):
    saved_tokens = {}
    teacher = {"id": "5035155459", "first_name": "Liandrei", "last_name": "Lumba"}

    def fake_create_token(token):
        saved_tokens[token["token_id"]] = token
        return token

    monkeypatch.setattr(qr_service.repository, "create_qr_token", fake_create_token)
    monkeypatch.setattr(qr_service.repository, "get_qr_token", lambda token_id: saved_tokens.get(token_id))
    monkeypatch.setattr(qr_service.repository, "get_teacher", lambda teacher_id: teacher if teacher_id == teacher["id"] else None)

    encoded, payload = qr_service.create_teacher_qr_payload(teacher, "admin-id")
    teacher_id, token_id = qr_service.validate_teacher_qr(encoded)

    assert teacher_id == "5035155459"
    assert token_id == payload["token_id"]


def test_validate_teacher_qr_rejects_unregistered_token(monkeypatch):
    teacher = {"id": "T-1", "first_name": "Test", "last_name": "Teacher"}
    monkeypatch.setattr(qr_service.repository, "create_qr_token", lambda token: token)
    monkeypatch.setattr(qr_service.repository, "get_qr_token", lambda token_id: None)

    encoded, _ = qr_service.create_teacher_qr_payload(teacher, "admin-id")

    with pytest.raises(qr_service.QRValidationError):
        qr_service.validate_teacher_qr(encoded)
