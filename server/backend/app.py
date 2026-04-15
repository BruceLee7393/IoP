import os

from flask import Flask, jsonify

from backend.auth.routes import auth_bp
from backend.common.bootstrap import ensure_database_ready
from backend.common.commands import register_commands
from backend.common.exceptions import ApiException
from backend.config import config_by_name
from backend.extensions import init_extensions
from backend.routes import role_bp, user_bp


def _import_all_models():
    # Force import of all domain model modules so metadata is fully registered.
    from backend.role import model as _role_model  # noqa: F401
    from backend.user import model as _user_model  # noqa: F401


def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv('FLASK_CONFIG', 'dev')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])

    _import_all_models()
    init_extensions(app)
    ensure_database_ready(app)

    @app.errorhandler(ApiException)
    def handle_api_exception(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({'code': 404, 'message': 'Not Found', 'data': None}), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500

    register_commands(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    return app
