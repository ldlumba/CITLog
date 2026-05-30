import base64
from io import BytesIO

import cv2
import numpy as np
import qrcode
from flask import Blueprint, jsonify, request, send_file

from audit import log_audit
import attendance_service
from auth_service import admin_required, current_admin
import qr_service
import repository


attendance_bp = Blueprint("attendance", __name__)


def decode_qr_from_data_url(data_url: str | None) -> str | None:
    if not data_url or "," not in data_url:
        return None
    try:
        _, encoded = data_url.split(",", 1)
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error):
        return None

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return None

    detector = cv2.QRCodeDetector()
    decoded_text, _, _ = detector.detectAndDecode(image)
    return decoded_text.strip() if decoded_text else None


def generate_qr_png(payload: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@attendance_bp.route("/time", methods=["POST"])
def log_time():
    data = request.get_json(silent=True) or {}
    try:
        _, teacher, signature = attendance_service.log_attendance(
            teacher_id=data.get("teacher_id"),
            action=data.get("action"),
            source="manual",
        )
    except attendance_service.AttendanceError as exc:
        return jsonify({"error": str(exc)}), 400
    except repository.RepositoryError:
        return jsonify({"error": "Attendance could not be saved."}), 502

    return jsonify({
        "message": f"{attendance_service.teacher_display_name(teacher)} recorded for {str(data.get('action')).upper()}.",
        "signature": signature,
        "teacher_name": attendance_service.teacher_display_name(teacher),
        "action": str(data.get("action")).upper(),
    }), 200


@attendance_bp.route("/scan-time", methods=["POST"])
def scan_time():
    data = request.get_json(silent=True) or {}
    qr_payload = str(data.get("qr_payload") or "").strip()
    qr_token_id = None

    try:
        if qr_payload:
            teacher_id, qr_token_id = qr_service.validate_teacher_qr(qr_payload)
        else:
            teacher_id = attendance_service.normalize_teacher_id(data.get("teacher_id"))

        action = attendance_service.next_scan_action(teacher_id)
        _, teacher, signature = attendance_service.log_attendance(
            teacher_id=teacher_id,
            action=action,
            source="qr" if qr_payload else "manual_scan_fallback",
            qr_token_id=qr_token_id,
        )
    except (attendance_service.AttendanceError, qr_service.QRValidationError) as exc:
        return jsonify({"error": str(exc)}), 400
    except repository.RepositoryError:
        return jsonify({"error": "Scanned attendance could not be saved."}), 502

    return jsonify({
        "message": f"{attendance_service.teacher_display_name(teacher)} recorded for {action}.",
        "teacher_id": str(teacher["id"]),
        "teacher_name": attendance_service.teacher_display_name(teacher),
        "action": action,
        "signature": signature,
    }), 200


@attendance_bp.route("/scan-frame", methods=["POST"])
def scan_frame():
    data = request.get_json(silent=True) or {}
    decoded_payload = decode_qr_from_data_url(data.get("image"))
    return jsonify({"qr_payload": decoded_payload}), 200


@attendance_bp.route("/verify", methods=["GET"])
@admin_required("view_attendance")
def verify_all():
    try:
        results = attendance_service.verified_attendance_rows()
    except repository.RepositoryError:
        return jsonify({"error": "Attendance records could not be loaded."}), 502
    log_audit("attendance.verify", "attendance", details={"count": len(results)})
    return jsonify(results), 200


@attendance_bp.route("/teachers", methods=["GET"])
@admin_required("list_teachers")
def list_teachers():
    try:
        teachers = [
            {
                "id": str(teacher["id"]),
                "name": attendance_service.teacher_display_name(teacher),
            }
            for teacher in repository.list_teachers()
        ]
    except repository.RepositoryError:
        return jsonify({"error": "Could not load teachers."}), 502
    return jsonify(teachers), 200


@attendance_bp.route("/teachers", methods=["POST"])
@admin_required("manage_teachers")
def create_teacher():
    data = request.get_json(silent=True) or {}
    teacher_id = str(data.get("id") or "").strip()
    first_name = str(data.get("first_name") or "").strip()
    last_name = str(data.get("last_name") or "").strip()

    if not teacher_id or not first_name or not last_name:
        return jsonify({"error": "ID, first name, and last name are required."}), 400
    if len(teacher_id) > 64 or len(first_name) > 120 or len(last_name) > 120:
        return jsonify({"error": "Teacher details exceed the allowed length."}), 400

    try:
        if repository.get_teacher(teacher_id):
            return jsonify({"error": "Teacher ID already exists."}), 400
        teacher = repository.create_teacher(teacher_id, first_name, last_name, current_admin()["id"])
    except repository.RepositoryError:
        return jsonify({"error": "Teacher could not be created."}), 502

    log_audit("teacher.create", "teacher", str(teacher_id), {"name": attendance_service.teacher_display_name(teacher)})
    return jsonify({
        "message": f"{attendance_service.teacher_display_name(teacher)} added successfully.",
        "teacher": {
            "id": str(teacher["id"]),
            "name": attendance_service.teacher_display_name(teacher),
        },
    }), 201


@attendance_bp.route("/teachers/<teacher_id>/qr", methods=["GET"])
@admin_required("generate_qr")
def teacher_qr(teacher_id):
    try:
        teacher = repository.get_teacher(teacher_id)
        if not teacher:
            return jsonify({"error": "Invalid Teacher ID."}), 404
        qr_payload, _ = qr_service.create_teacher_qr_payload(teacher, current_admin()["id"])
    except repository.RepositoryError:
        return jsonify({"error": "QR token could not be created."}), 502

    log_audit("qr.generate", "teacher", str(teacher_id))
    return jsonify({
        "teacher_id": str(teacher["id"]),
        "name": attendance_service.teacher_display_name(teacher),
        "qr_image_url": f"/teachers/{teacher_id}/qr.png?payload={qr_payload}",
        "download_url": f"/teachers/{teacher_id}/qr.png?download=1&payload={qr_payload}",
        "filename": f"teacher_{teacher_id}_qr.png",
    }), 200


@attendance_bp.route("/teachers/<teacher_id>/qr.png", methods=["GET"])
@admin_required("generate_qr")
def teacher_qr_png(teacher_id):
    payload = str(request.args.get("payload") or "").strip()
    try:
        validated_teacher_id, _ = qr_service.validate_teacher_qr(payload)
    except qr_service.QRValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    if str(validated_teacher_id) != str(teacher_id):
        return jsonify({"error": "QR payload does not match the requested teacher."}), 400

    filename = f"teacher_{teacher_id}_qr.png"
    return send_file(
        generate_qr_png(payload),
        mimetype="image/png",
        as_attachment=request.args.get("download") == "1",
        download_name=filename,
    )


@attendance_bp.route("/attendance/clear", methods=["POST"])
@admin_required("clear_attendance")
def clear_attendance():
    try:
        cleared_count = repository.clear_attendance()
    except repository.RepositoryError:
        return jsonify({"error": "Attendance records could not be cleared."}), 502

    log_audit("attendance.clear", "attendance", details={"cleared_count": cleared_count})
    if not cleared_count:
        return jsonify({"message": "There are no attendance records to clear."}), 200
    return jsonify({"message": f"{cleared_count} attendance record(s) cleared successfully."}), 200
