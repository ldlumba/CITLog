import copy

import crypto


def test_sign_and_verify_payload():
    payload = {"teacher_id": "5035155459", "date": "2026-04-09", "time": "08:00:00", "action": "IN"}

    signature = crypto.sign_payload(payload)

    assert crypto.verify_payload(payload, signature) is True


def test_tampered_payload_fails_verification():
    payload = {"teacher_id": "5035155459", "date": "2026-04-09", "time": "08:00:00", "action": "IN"}
    signature = crypto.sign_payload(payload)
    tampered = copy.deepcopy(payload)
    tampered["action"] = "OUT"

    assert crypto.verify_payload(tampered, signature) is False


def test_signed_envelope_round_trip():
    payload = {"v": 1, "typ": "teacher_attendance_qr", "token_id": "abc", "teacher_id": "T-1"}

    encoded = crypto.encode_signed_envelope(payload)

    assert encoded.startswith("CITLOG1.")
    assert crypto.decode_signed_envelope(encoded) == payload
