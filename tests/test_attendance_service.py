import attendance_service
import crypto


def test_log_attendance_signs_canonical_payload(monkeypatch):
    inserted_rows = []

    monkeypatch.setattr(attendance_service.repository, "get_teacher", lambda teacher_id: {
        "id": teacher_id,
        "first_name": "Liandrei",
        "last_name": "Lumba",
    })

    def fake_insert(row):
        inserted_rows.append(row)
        return {"id": 1, **row}

    monkeypatch.setattr(attendance_service.repository, "insert_attendance", fake_insert)

    inserted, teacher, signature = attendance_service.log_attendance("5035155459", "IN", "manual")

    assert inserted["teacher_id"] == "5035155459"
    assert teacher["first_name"] == "Liandrei"
    assert signature == inserted_rows[0]["signature"]
    assert attendance_service.verify_attendance_entry(inserted) is True


def test_verify_attendance_rejects_modified_signed_field(monkeypatch):
    monkeypatch.setattr(attendance_service.repository, "get_teacher", lambda teacher_id: {
        "id": teacher_id,
        "first_name": "Caryl",
        "last_name": "Dizon",
    })
    monkeypatch.setattr(attendance_service.repository, "insert_attendance", lambda row: {"id": 1, **row})

    inserted, _, _ = attendance_service.log_attendance("5035155459", "IN", "manual")
    inserted["time"] = "09:30:00"

    assert attendance_service.verify_attendance_entry(inserted) is False


def test_verify_attendance_rejects_hash_mismatch():
    payload = {"teacher_id": "T1", "date": "2026-04-09", "time": "08:00:00", "action": "IN"}
    entry = {
        **payload,
        "signature": crypto.sign_payload(payload),
        "payload_hash": "not-the-real-hash",
    }

    assert attendance_service.verify_attendance_entry(entry) is False
