from datetime import timedelta

from flask import Flask, jsonify, render_template, request

from audit import log_audit
from auth_service import AuthError, login_admin, logout_admin, page_admin_required
from config import settings
import repository
from routes.attendance import attendance_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.secret_key
    app.permanent_session_lifetime = timedelta(hours=settings.session_hours)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.secure_cookies,
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,
    )

    app.register_blueprint(attendance_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/admin")
    @page_admin_required
    def admin():
        return render_template("admin.html")

    @app.route("/admin/login", methods=["POST"])
    def admin_login():
        data = request.get_json(silent=True) or {}
        try:
            admin_user = login_admin(data.get("username", ""), data.get("password", ""))
        except AuthError as exc:
            log_audit("admin.login_failed", "admin_user", details={"username": str(data.get("username", ""))[:120]})
            return jsonify({"error": str(exc)}), 401
        except repository.RepositoryError:
            return jsonify({"error": "Admin authentication is temporarily unavailable."}), 502

        log_audit("admin.login_success", "admin_user", admin_user["id"])
        return jsonify({"message": "Admin access granted.", "admin": admin_user}), 200

    @app.route("/admin/logout", methods=["POST"])
    def admin_logout():
        log_audit("admin.logout", "admin_user")
        logout_admin()
        return jsonify({"message": "Logged out."}), 200

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"error": "Uploaded frame is too large."}), 413

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Unexpected server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
