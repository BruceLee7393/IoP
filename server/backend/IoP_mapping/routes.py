from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from backend.IoP_mapping.model import Permission, RoleMappingPermission
from backend.IoP_role.model import Role
from backend.extensions import db


IoP_mapping_bp = Blueprint('IoP_mapping', __name__, url_prefix='/api/iop/mapping')
IoP_mapping_compat_bp = Blueprint('IoP_mapping_compat', __name__, url_prefix='/api/roles/permissions')


def _success(data, message='操作成功', status=200):
    return jsonify({'code': 0, 'message': message, 'data': data}), status


def _error(message, status):
    return jsonify({'code': status, 'message': message, 'data': None}), status


@IoP_mapping_bp.route('/permissions', methods=['GET'])
@IoP_mapping_compat_bp.route('', methods=['GET'])
def list_permissions():
    permissions = Permission.query.order_by(Permission.permission_code.asc()).all()
    data = [
        {
            'id': item.id,
            'permission_code': item.permission_code,
            'permission_name': item.permission_name,
            'description': item.description,
        }
        for item in permissions
    ]
    return _success(data, message='获取权限列表成功')


@IoP_mapping_bp.route('/role/<string:role_id>/permissions', methods=['GET'])
def list_role_permissions(role_id):
    permission_ids = [
        item[0]
        for item in (
            RoleMappingPermission.query.with_entities(RoleMappingPermission.permission_id)
            .filter(RoleMappingPermission.role_id == role_id)
            .distinct()
            .order_by(RoleMappingPermission.permission_id.asc())
            .all()
        )
    ]

    return _success(
        {
            'role_id': role_id,
            'permission_ids': permission_ids,
        },
        message='获取角色权限成功',
    )


@IoP_mapping_compat_bp.route('/<string:role_id>', methods=['GET'])
def list_role_permissions_compat(role_id):
    rows = (
        db.session.query(Permission)
        .join(RoleMappingPermission, RoleMappingPermission.permission_id == Permission.id)
        .filter(RoleMappingPermission.role_id == role_id)
        .order_by(Permission.permission_code.asc())
        .all()
    )

    data = [
        {
            'id': item.id,
            'permission_code': item.permission_code,
            'permission_name': item.permission_name,
            'description': item.description,
        }
        for item in rows
    ]
    return _success(data, message='获取角色权限成功')


@IoP_mapping_bp.route('/role/<string:role_id>/permissions', methods=['PUT'])
def update_role_permissions(role_id):
    payload = request.get_json(silent=True) or {}
    permission_ids = payload.get('permission_ids')

    if not isinstance(permission_ids, list):
        return _error('permission_ids 必须是数组', 400)

    normalized_permission_ids = []
    seen = set()
    for item in permission_ids:
        if not isinstance(item, str) or not item.strip():
            return _error('permission_ids 中的每一项都必须是非空字符串', 400)
        pid = item.strip()
        if pid not in seen:
            seen.add(pid)
            normalized_permission_ids.append(pid)

    role_exists = Role.query.with_entities(Role.id).filter(Role.id == role_id).first()
    if not role_exists:
        return _error('角色不存在', 404)

    if normalized_permission_ids:
        existed_permission_ids = {
            row[0]
            for row in (
                Permission.query.with_entities(Permission.id)
                .filter(Permission.id.in_(normalized_permission_ids))
                .all()
            )
        }
        missing_permission_ids = sorted(set(normalized_permission_ids) - existed_permission_ids)
        if missing_permission_ids:
            return _error(f'权限不存在: {", ".join(missing_permission_ids)}', 400)

    try:
        # Explicitly open a nested transaction to enforce atomic update semantics.
        tx = db.session.begin_nested()

        RoleMappingPermission.query.filter(RoleMappingPermission.role_id == role_id).delete(
            synchronize_session=False
        )

        if normalized_permission_ids:
            db.session.add_all(
                [
                    RoleMappingPermission(role_id=role_id, permission_id=permission_id)
                    for permission_id in normalized_permission_ids
                ]
            )

        tx.commit()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _error('分配权限失败，数据库事务已回滚', 500)
    except Exception:
        db.session.rollback()
        return _error('分配权限失败，发生未知错误', 500)

    return _success(
        {
            'role_id': role_id,
            'permission_ids': normalized_permission_ids,
        },
        message='分配权限成功',
    )


def _validate_role_and_permission_ids(role_id, permission_ids):
    if not isinstance(permission_ids, list):
        return None, _error('permission_ids 必须是数组', 400)

    normalized_permission_ids = []
    seen = set()
    for item in permission_ids:
        if not isinstance(item, str) or not item.strip():
            return None, _error('permission_ids 中的每一项都必须是非空字符串', 400)
        pid = item.strip()
        if pid not in seen:
            seen.add(pid)
            normalized_permission_ids.append(pid)

    role_exists = Role.query.with_entities(Role.id).filter(Role.id == role_id).first()
    if not role_exists:
        return None, _error('角色不存在', 404)

    if normalized_permission_ids:
        existed_permission_ids = {
            row[0]
            for row in (
                Permission.query.with_entities(Permission.id)
                .filter(Permission.id.in_(normalized_permission_ids))
                .all()
            )
        }
        missing_permission_ids = sorted(set(normalized_permission_ids) - existed_permission_ids)
        if missing_permission_ids:
            return None, _error(f'权限不存在: {", ".join(missing_permission_ids)}', 400)

    return normalized_permission_ids, None


@IoP_mapping_compat_bp.route('/<string:role_id>/batch-add', methods=['POST'])
def add_role_permissions_compat(role_id):
    payload = request.get_json(silent=True) or {}
    normalized_permission_ids, error_resp = _validate_role_and_permission_ids(
        role_id,
        payload.get('permission_ids'),
    )
    if error_resp:
        return error_resp

    try:
        tx = db.session.begin_nested()
        existed_ids = {
            row[0]
            for row in (
                RoleMappingPermission.query.with_entities(RoleMappingPermission.permission_id)
                .filter(RoleMappingPermission.role_id == role_id)
                .all()
            )
        }
        to_insert = [
            RoleMappingPermission(role_id=role_id, permission_id=permission_id)
            for permission_id in normalized_permission_ids
            if permission_id not in existed_ids
        ]
        if to_insert:
            db.session.add_all(to_insert)
        tx.commit()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _error('分配权限失败，数据库事务已回滚', 500)
    except Exception:
        db.session.rollback()
        return _error('分配权限失败，发生未知错误', 500)

    return _success({'role_id': role_id, 'permission_ids': normalized_permission_ids}, message='分配权限成功')


@IoP_mapping_compat_bp.route('/<string:role_id>/batch-delete', methods=['DELETE'])
def remove_role_permissions_compat(role_id):
    payload = request.get_json(silent=True) or {}
    normalized_permission_ids, error_resp = _validate_role_and_permission_ids(
        role_id,
        payload.get('permission_ids'),
    )
    if error_resp:
        return error_resp

    try:
        tx = db.session.begin_nested()
        if normalized_permission_ids:
            RoleMappingPermission.query.filter(
                RoleMappingPermission.role_id == role_id,
                RoleMappingPermission.permission_id.in_(normalized_permission_ids),
            ).delete(synchronize_session=False)
        tx.commit()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return _error('分配权限失败，数据库事务已回滚', 500)
    except Exception:
        db.session.rollback()
        return _error('分配权限失败，发生未知错误', 500)

    return _success({'role_id': role_id, 'permission_ids': normalized_permission_ids}, message='分配权限成功')
