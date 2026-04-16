from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from backend.auth.service import auth_service
from backend.common.exceptions import InvalidUsageError


IoP_auth_bp = Blueprint('IoP_auth', __name__, url_prefix='/api/iop/auth')
IoP_auth_compat_bp = Blueprint('IoP_auth_compat', __name__, url_prefix='/api/auth')


def _extract_bearer_token(auth_header):
    if not auth_header:
        return None
    parts = str(auth_header).split(' ', 1)
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        token = parts[1].strip()
        return token or None
    return None


@IoP_auth_compat_bp.route('/login', methods=['POST'])
@IoP_auth_bp.route('/login', methods=['POST'])
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


@IoP_auth_compat_bp.route('/logout', methods=['POST'])
@IoP_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jwt_payload = get_jwt() or {}
    user_id = get_jwt_identity()
    jti = str(jwt_payload.get('jti', '')).strip()
    exp_ts = jwt_payload.get('exp')

    if not jti:
        raise InvalidUsageError('无效的登录凭证')

    token = _extract_bearer_token(request.headers.get('Authorization'))
    auth_service.logout(user_id=user_id, jti=jti, exp_ts=exp_ts, access_token=token)

    return jsonify({'code': 200, 'message': '登出成功', 'data': None}), 200
