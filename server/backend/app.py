import os
from urllib.parse import quote_plus

from flask import Flask, jsonify

from backend.auth.routes import auth_bp
from backend.commands import register_commands
from backend.common.exceptions import ApiException
from backend.config import config_by_name
from backend.extensions import init_extensions


def _build_runtime_db_uri():
    db_user = os.getenv('DB_USER', 'root')
    db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'IoP')
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = _build_runtime_db_uri()
    app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])

    init_extensions(app)

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
    return app
