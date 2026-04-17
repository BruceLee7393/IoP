from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoP_mapping import service as mapping_service


IoP_mapping_bp = Blueprint('IoP_mapping', __name__, url_prefix='/api/iop/mapping')
IoP_mapping_compat_bp = Blueprint('IoP_mapping_compat', __name__, url_prefix='/api/roles/permissions')


@IoP_mapping_bp.route('/permissions', methods=['GET'])
@IoP_mapping_compat_bp.route('', methods=['GET'])
@jwt_required
def list_permissions():
    data = mapping_service.list_permissions_tree()
    return ok(data=data, message='获取权限树成功', status=200)


@IoP_mapping_bp.route('/permissions/current', methods=['GET'])
@IoP_mapping_compat_bp.route('/current', methods=['GET'])
@jwt_required()
def list_current_user_permissions():
    user_id = get_jwt_identity()
    data = mapping_service.list_current_user_permissions(user_id)
    return ok(data=data, message='获取当前用户权限成功', status=200)


@IoP_mapping_bp.route('/role/<string:role_id>/permissions', methods=['GET'])
@jwt_required
def list_role_permissions(role_id):
    data = mapping_service.list_role_permission_ids(role_id)
    return ok(data=data, message='获取角色权限成功', status=200)


@IoP_mapping_compat_bp.route('/<string:role_id>', methods=['GET'])
@jwt_required
def list_role_permissions_compat(role_id):
    data = mapping_service.list_role_permissions(role_id)
    return ok(data=data, message='获取角色权限成功', status=200)


@IoP_mapping_bp.route('/role/<string:role_id>/permissions', methods=['PUT'])
@jwt_required
def update_role_permissions(role_id):
    payload = request.get_json(silent=True) or {}
    data = mapping_service.replace_role_permissions(role_id, payload.get('permission_ids'))
    return ok(data=data, message='分配权限成功', status=200)


@IoP_mapping_compat_bp.route('/<string:role_id>/batch-add', methods=['POST'])
@jwt_required
def add_role_permissions_compat(role_id):
    payload = request.get_json(silent=True) or {}
    data = mapping_service.add_role_permissions(role_id, payload.get('permission_ids'))
    return ok(data=data, message='分配权限成功', status=200)


@IoP_mapping_compat_bp.route('/<string:role_id>/batch-delete', methods=['DELETE'])
@jwt_required
def remove_role_permissions_compat(role_id):
    payload = request.get_json(silent=True) or {}
    data = mapping_service.remove_role_permissions(role_id, payload.get('permission_ids'))
    return ok(data=data, message='分配权限成功', status=200)
