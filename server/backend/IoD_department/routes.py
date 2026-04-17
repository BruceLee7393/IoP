from flask import Blueprint, request

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoD_department import service as department_service


IoD_department_bp = Blueprint('IoD_department', __name__, url_prefix='/api/iod/department')


@IoD_department_bp.route('', methods=['GET'])
@jwt_required
def list_departments():
    data = department_service.list_departments(request.args)
    return ok(data=data, message='获取部门列表成功', status=200)


@IoD_department_bp.route('/<string:dept_id>', methods=['GET'])
@jwt_required
def get_department(dept_id):
    data = department_service.get_department_detail(dept_id)
    return ok(data=data, message='获取部门详情成功', status=200)


@IoD_department_bp.route('', methods=['POST'])
@jwt_required
def create_department():
    payload = request.get_json(silent=True) or {}
    data = department_service.create_department(payload)
    return ok(data=data, message='新增部门成功', status=201)


@IoD_department_bp.route('/<string:dept_id>', methods=['PUT', 'PATCH'])
@jwt_required
def update_department(dept_id):
    payload = request.get_json(silent=True) or {}
    data = department_service.update_department(dept_id, payload)
    return ok(data=data, message='更新部门成功', status=200)


@IoD_department_bp.route('/<string:dept_id>', methods=['DELETE'])
@jwt_required
def delete_department(dept_id):
    data = department_service.delete_department(dept_id)
    return ok(data=data, message='删除部门成功', status=200)
