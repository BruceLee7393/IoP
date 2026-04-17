from flask import Blueprint, request

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoP_user import service as user_service

IoP_user_bp = Blueprint('IoP_user', __name__, url_prefix='/api/iop/user')
IoP_user_compat_bp = Blueprint('IoP_user_compat', __name__, url_prefix='/api/users')


@IoP_user_compat_bp.route('', methods=['POST'])
@IoP_user_bp.route('', methods=['POST'])
@jwt_required
def create_user():
    payload = request.get_json(silent=True) or {}
    data = user_service.create_user(payload)
    return ok(data=data, message='新增用户成功', status=200)


@IoP_user_compat_bp.route('/register', methods=['POST'])
@IoP_user_bp.route('/register', methods=['POST'])
@jwt_required
def create_user_register():
    payload = request.get_json(silent=True) or {}
    data = user_service.create_user(payload)
    return ok(data=data, message='新增用户成功', status=200)


@IoP_user_compat_bp.route('', methods=['GET'])
@IoP_user_bp.route('', methods=['GET'])
@jwt_required
def list_users():
    data = user_service.list_users(request.args)
    return ok(data=data, message='获取用户列表成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>', methods=['GET'])
@IoP_user_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    data = user_service.get_user_detail(user_id)
    return ok(data=data, message='获取用户详情成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>', methods=['PUT', 'PATCH'])
@IoP_user_bp.route('/<string:user_id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    data = user_service.update_user(user_id, payload)
    return ok(data=data, message='更新用户成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>/status', methods=['PATCH'])
@IoP_user_bp.route('/<string:user_id>/status', methods=['PATCH'])
@jwt_required
def toggle_user_status(user_id):
    payload = request.get_json(silent=True) or {}
    status = str(payload.get('status', '')).strip()
    data = user_service.toggle_user_status(user_id, status)
    return ok(data=data, message='更新用户状态成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>/reset-password', methods=['PATCH'])
@IoP_user_bp.route('/<string:user_id>/reset-password', methods=['PATCH'])
@jwt_required
def reset_password(user_id):
    payload = request.get_json(silent=True) or {}
    data = user_service.reset_user_password(user_id, payload.get('password'))
    return ok(data=data, message='用户密码重置成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>/password-reset', methods=['POST'])
@IoP_user_bp.route('/<string:user_id>/password-reset', methods=['POST'])
@jwt_required
def reset_password_compat(user_id):
    payload = request.get_json(silent=True) or {}
    if 'newPassword' in payload and 'password' not in payload:
        payload = {'password': payload.get('newPassword')}
    data = user_service.reset_user_password(user_id, payload.get('password'))
    return ok(data=data, message='用户密码重置成功', status=200)


@IoP_user_compat_bp.route('/<string:user_id>', methods=['DELETE'])
@IoP_user_bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    data = user_service.delete_user(user_id)
    return ok(data=data, message='删除用户成功', status=200)
