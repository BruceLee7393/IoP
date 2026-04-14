from flask import Flask, jsonify
from werkzeug.exceptions import UnprocessableEntity
import os

from backend.config import config_by_name
from backend.extensions import init_extensions
# [新增] 导入自定义异常基类和蓝图
from backend.common.exceptions import ApiException
from backend.user.routes import user_bp
from backend.auth.routes import auth_bp
from backend.role.routes import role_bp
from backend.order.routes import order_bp
from backend.user.model import User
from backend.role.model import Role
import logging

def create_app(config_name='dev'):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # [新增] 为 Flask-JWT-Extended 设置密钥
    # 推荐在 .env 中单独设置 JWT_SECRET_KEY，如果没有，则使用通用的 SECRET_KEY
    app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])

    init_extensions(app)

   


    # [新增] 注册全局的 ApiException 处理器
    @app.errorhandler(ApiException)
    def handle_api_exception(error):
        """这是一个捕获所有 ApiException 子类异常的处理器"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # [新增] 注册 webargs 的 422 错误处理器
    @app.errorhandler(422)
    @app.errorhandler(UnprocessableEntity)
    def handle_webargs_error(error):
        """捕获 webargs 的验证错误，并返回统一的 JSON 格式"""
        # error.data['messages'] 包含了 webargs 提供的详细错误信息
        # 我们把它重命名为 'errors' 以符合通用的 API 错误格式
        error_messages = error.data.get('messages', {}) if hasattr(error, 'data') else {}
        response_data = {
            "message": "Invalid parameters",
            "errors": error_messages
        }
        response = jsonify(response_data)
        response.status_code = 422
        return response

    # [新增] 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(order_bp)

    # 初始化上传目录
    if 'UPLOAD_FOLDER' in app.config:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if 'SOFTWARE_UPLOAD_FOLDER' in app.config:
        os.makedirs(app.config['SOFTWARE_UPLOAD_FOLDER'], exist_ok=True)

    return app
