from flask import Blueprint, jsonify, request

from backend.auth.service import auth_service
from backend.common.exceptions import InvalidUsageError


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True)
    if not payload:
        raise InvalidUsageError('请求体不能为空')

    account = str(payload.get('account', '')).strip()
    password = str(payload.get('password', '')).strip()

    if not account or not password:
        raise InvalidUsageError('用户账号和密码是必需的')

    token, user_info = auth_service.login(account, password)
    return jsonify({'code': 200, 'message': 'success', 'data': {'token': token, 'userInfo': user_info}}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'code': 200, 'message': 'success', 'data': None}), 200
