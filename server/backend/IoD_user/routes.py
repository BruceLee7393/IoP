from flask import Blueprint, request

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoD_user import service as user_service


IoD_user_bp = Blueprint('IoD_user', __name__, url_prefix='/api/iod/user')


@IoD_user_bp.route('', methods=['GET'])
@jwt_required
def list_users():
    data = user_service.list_users(request.args)
    return ok(data=data, message='获取用户列表成功', status=200)


@IoD_user_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    data = user_service.get_user_detail(user_id)
    return ok(data=data, message='获取用户详情成功', status=200)


@IoD_user_bp.route('', methods=['POST'])
@jwt_required
def create_user():
    payload = request.get_json(silent=True) or {}
    data = user_service.create_user(payload)
    return ok(data=data, message='新增用户成功', status=201)


@IoD_user_bp.route('/<string:user_id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    data = user_service.update_user(user_id, payload)
    return ok(data=data, message='更新用户成功', status=200)


@IoD_user_bp.route('/<string:user_id>/status', methods=['PATCH'])
@jwt_required
def change_user_status(user_id):
    payload = request.get_json(silent=True) or {}
    data = user_service.change_user_status(user_id, payload.get('status'))
    return ok(data=data, message='更新用户状态成功', status=200)


@IoD_user_bp.route('/<string:user_id>/reset-password', methods=['PATCH'])
@jwt_required
def reset_password(user_id):
    payload = request.get_json(silent=True) or {}
    data = user_service.reset_user_password(user_id, payload.get('password'))
    return ok(data=data, message='重置密码成功', status=200)


@IoD_user_bp.route('/<string:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    data = user_service.delete_user(user_id)
    return ok(data=data, message='删除用户成功', status=200)
