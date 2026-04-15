from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.role.model import Role, RoleMappingPermission
from backend.user.model import User

role_bp = Blueprint('role', __name__, url_prefix='/api/roles')


def _role_to_dict(role):
    return {
        'id': role.id,
        'role_code': role.role_code,
        'role_name': role.role_name,
        'description': role.description,
        'status': role.status,
        'extra_data': role.extra_data,
        'created_at': role.created_at.isoformat() if role.created_at else None,
        'updated_at': role.updated_at.isoformat() if role.updated_at else None,
    }


def _success(data, message='操作成功', status=200):
    return jsonify({'code': 0, 'message': message, 'data': data}), status


def _error(message, status):
    return jsonify({'code': status, 'message': message, 'data': None}), status


@role_bp.route('', methods=['POST'])
def create_role():
    payload = request.get_json(silent=True) or {}

    role_code = str(payload.get('role_code', '')).strip()
    role_name = str(payload.get('role_name', '')).strip()
    description = payload.get('description')
    status = str(payload.get('status', 'active')).strip() or 'active'
    extra_data = payload.get('extra_data')

    if not role_code or not role_name:
        return _error('role_code 和 role_name 是必填项', 400)
    if status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

    existed = Role.query.filter(Role.role_code == role_code).first()
    if existed:
        return _error('角色编码已存在', 409)

    role = Role(
        role_code=role_code,
        role_name=role_name,
        description=description,
        status=status,
        extra_data=extra_data,
    )

    try:
        db.session.add(role)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error('角色编码已存在', 409)
    except Exception:
        db.session.rollback()
        return _error('创建角色失败，发生未知错误。', 500)

    return _success(_role_to_dict(role), message='新增角色成功', status=201)


@role_bp.route('', methods=['GET'])
def list_roles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)

    role_code = request.args.get('role_code', type=str)
    role_name = request.args.get('role_name', type=str)
    status = request.args.get('status', type=str)

    if page <= 0 or per_page <= 0:
        return _error('page 和 per_page 必须大于 0', 400)
    if status and status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

    query = Role.query

    if role_code:
        query = query.filter(Role.role_code.like(f'{role_code}%'))
    if role_name:
        query = query.filter(Role.role_name.like(f'%{role_name}%'))
    if status:
        query = query.filter(Role.status == status)

    sort_map = {
        'role_code': Role.role_code,
        'role_name': Role.role_name,
        'status': Role.status,
        'created_at': Role.created_at,
        'updated_at': Role.updated_at,
    }
    sort_col = sort_map.get(sort_by, Role.created_at)
    query = query.order_by(sort_col.asc() if sort_order == 'asc' else sort_col.desc())

    paged = query.paginate(page=page, per_page=per_page, error_out=False)

    return _success(
        {
            'items': [_role_to_dict(item) for item in paged.items],
            'pagination': {
                'total': paged.total,
                'pages': paged.pages,
                'page': paged.page,
                'per_page': paged.per_page,
            },
        },
        message='获取角色列表成功',
    )


@role_bp.route('/<string:role_id>', methods=['GET'])
def get_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        return _error('角色不存在', 404)
    return _success(_role_to_dict(role), message='获取角色详情成功')


@role_bp.route('/<string:role_id>', methods=['PUT', 'PATCH'])
def update_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        return _error('角色不存在', 404)

    payload = request.get_json(silent=True) or {}

    if 'role_code' in payload:
        role_code = str(payload.get('role_code', '')).strip()
        if not role_code:
            return _error('role_code 不能为空', 400)
        duplicated = Role.query.filter(Role.role_code == role_code, Role.id != role.id).first()
        if duplicated:
            return _error('角色编码已存在', 409)
        role.role_code = role_code

    if 'role_name' in payload:
        role_name = str(payload.get('role_name', '')).strip()
        if not role_name:
            return _error('role_name 不能为空', 400)
        role.role_name = role_name

    if 'description' in payload:
        role.description = payload.get('description')

    if 'status' in payload:
        status = str(payload.get('status', '')).strip()
        if status not in {'active', 'disabled'}:
            return _error('status 仅支持 active 或 disabled', 400)
        role.status = status

    if 'extra_data' in payload:
        role.extra_data = payload.get('extra_data')

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error('角色编码已存在', 409)
    except Exception:
        db.session.rollback()
        return _error('更新角色失败，发生未知错误。', 500)

    return _success(_role_to_dict(role), message='更新角色成功')


@role_bp.route('/<string:role_id>/status', methods=['PATCH'])
def toggle_role_status(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        return _error('角色不存在', 404)

    payload = request.get_json(silent=True) or {}
    status = str(payload.get('status', '')).strip()
    if status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

    role.status = status
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('状态更新失败，发生未知错误。', 500)

    return _success(_role_to_dict(role), message='更新角色状态成功')


@role_bp.route('/<string:role_id>', methods=['DELETE'])
def delete_role(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        return _error('角色不存在', 404)

    related_user_count = User.query.filter(User.role_id == role_id).count()
    if related_user_count > 0:
        return _error('无法删除该角色，请先取消相关用户的角色关联', 400)

    related_permission_count = RoleMappingPermission.query.filter(
        RoleMappingPermission.role_id == role_id
    ).count()
    if related_permission_count > 0:
        return _error('该角色存在关联权限，禁止删除', 400)

    try:
        db.session.delete(role)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('删除角色失败，发生未知错误。', 500)

    return _success({'deleted': True, 'role_id': role_id}, message='删除角色成功')
