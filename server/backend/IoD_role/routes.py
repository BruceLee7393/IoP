from flask import Blueprint, request

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoD_role import service as role_service


IoD_role_bp = Blueprint('IoD_role', __name__, url_prefix='/api/iod/role')


@IoD_role_bp.route('', methods=['GET'])
@jwt_required
def list_roles():
    data = role_service.list_roles(request.args)
    return ok(data=data, message='获取角色列表成功', status=200)


@IoD_role_bp.route('/<string:role_id>', methods=['GET'])
@jwt_required
def get_role(role_id):
    data = role_service.get_role_detail(role_id)
    return ok(data=data, message='获取角色详情成功', status=200)


@IoD_role_bp.route('', methods=['POST'])
@jwt_required
def create_role():
    payload = request.get_json(silent=True) or {}
    data = role_service.create_role(payload)
    return ok(data=data, message='新增角色成功', status=201)


@IoD_role_bp.route('/<string:role_id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_role(role_id):
    payload = request.get_json(silent=True) or {}
    data = role_service.update_role(role_id, payload)
    return ok(data=data, message='更新角色成功', status=200)


@IoD_role_bp.route('/<string:role_id>/status', methods=['PATCH'])
@jwt_required
def change_role_status(role_id):
    payload = request.get_json(silent=True) or {}
    data = role_service.change_role_status(role_id, payload.get('status'))
    return ok(data=data, message='更新角色状态成功', status=200)


@IoD_role_bp.route('/<string:role_id>', methods=['DELETE'])
@jwt_required
def delete_role(role_id):
    data = role_service.delete_role(role_id)
    return ok(data=data, message='删除角色成功', status=200)
