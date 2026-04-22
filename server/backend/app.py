import os

from flask import Flask, jsonify  # pyright: ignore[reportMissingImports]

from backend.IoD_dashboard.routes import IoD_dashboard_bp
from backend.IoD_department.routes import IoD_department_bp
from backend.IoD_role.routes import IoD_role_bp
from backend.IoD_user.routes import IoD_user_bp
from backend.IoP_mapping.routes import IoP_mapping_bp, IoP_mapping_compat_bp
from backend.auth.routes import IoP_auth_bp, IoP_auth_compat_bp
from backend.common.bootstrap import ensure_database_ready
from backend.common.commands import register_commands
from backend.common.exceptions import ApiException
from backend.config import config_by_name
from backend.extensions import init_extensions, jwt, redis_client
from backend.routes import (
    IoP_role_bp,
    IoP_role_compat_bp,
    IoP_user_bp,
    IoP_user_compat_bp,
)


def _import_all_models():
    # Force import of all domain model modules so metadata is fully registered.
    from backend.IoD_department import model as _iod_department_model  # noqa: F401
    from backend.IoD_mapping import model as _iod_mapping_model  # noqa: F401
    from backend.IoD_role import model as _iod_role_model  # noqa: F401
    from backend.IoD_user import model as _iod_user_model  # noqa: F401
    from backend.IoP_mapping import model as _mapping_model  # noqa: F401
    from backend.IoP_role import model as _role_model  # noqa: F401
    from backend.IoP_user import model as _user_model  # noqa: F401


def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv("FLASK_CONFIG", "dev")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config.setdefault("JWT_SECRET_KEY", app.config["SECRET_KEY"])

    _import_all_models()
    init_extensions(app)

    @jwt.token_in_blocklist_loader
    def _is_token_revoked(_jwt_header, jwt_payload):
        jti = str((jwt_payload or {}).get("jti", "")).strip()
        if not jti:
            return True

        token_type = str(
            (jwt_payload or {}).get("token_type")
            or (jwt_payload or {}).get("type")
            or ""
        ).strip()

        if redis_client.get(f"blacklisted_token:{jti}"):
            return True

        if token_type == "refresh":
            return redis_client.get(f"refresh_token:{jti}") is None

        return redis_client.get(f"login_token:{jti}") is None

    ensure_database_ready(app)

    @app.errorhandler(ApiException)
    def handle_api_exception(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"code": 404, "message": "Not Found", "data": None}), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify({"code": 500, "message": "服务器内部错误", "data": None}), 500

    register_commands(app)
    app.register_blueprint(IoP_mapping_bp)
    app.register_blueprint(IoP_mapping_compat_bp)
    app.register_blueprint(IoP_auth_bp)
    app.register_blueprint(IoP_auth_compat_bp)
    app.register_blueprint(IoP_user_bp)
    app.register_blueprint(IoP_user_compat_bp)
    app.register_blueprint(IoP_role_bp)
    app.register_blueprint(IoP_role_compat_bp)
    app.register_blueprint(IoD_dashboard_bp)
    app.register_blueprint(IoD_role_bp)
    app.register_blueprint(IoD_department_bp)
    app.register_blueprint(IoD_user_bp)
    return app
