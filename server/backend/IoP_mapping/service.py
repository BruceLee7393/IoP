from collections import OrderedDict

from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import db
from backend.IoP_mapping.model import Permission, RoleMappingPermission
from backend.IoP_role.model import Role
from backend.IoP_user.model import User


def _safe_label(value):
    text = str(value or '').strip()
    if not text:
        return '未命名'
    return text.replace('_', ' ').replace('-', ' ').title()


def _system_label(system_code):
    code = str(system_code or '').strip().lower()
    if code == 'iop':
        return 'IoP 系统管理'
    if code == 'iod':
        return 'IoD 系统管理'
    return f'{_safe_label(system_code)} 系统管理'


def _is_home_permission(permission):
    permission_code = str(getattr(permission, 'permission_code', '') or '').strip().lower()
    permission_name = str(getattr(permission, 'permission_name', '') or '').strip().lower()
    if permission_name == '首页':
        return True
    if permission_code in {'home', 'index', 'dashboard'}:
        return True
    segments = [segment for segment in permission_code.split(':') if segment]
    return any(segment in {'home', 'index', 'dashboard'} for segment in segments)


def _permission_to_dict(item):
    return {
        'id': item.id,
        'permission_code': item.permission_code,
        'permission_name': item.permission_name,
        'description': item.description,
    }


def _is_admin_account(account):
    value = str(account or '').strip().lower()
    return value in {'admin', 'administrator', 'root'} or 'admin' in value


def _is_admin_role_id(role_id):
    role = (
        Role.query.with_entities(Role.role_code, Role.role_name)
        .filter(Role.id == role_id)
        .first()
    )
    if not role:
        return False

    role_code = str(role[0] or '').strip().lower()
    role_name = str(role[1] or '').strip().lower()

    admin_codes = {'admin', 'administrator', 'superadmin', 'super_admin', 'root'}
    admin_names = {'管理员', '系统管理员'}

    if role_code in admin_codes or 'admin' in role_code:
        return True
    return role_name in admin_names or '管理员' in role_name


def _get_all_non_home_permissions():
    permissions = Permission.query.order_by(Permission.permission_code.asc()).all()
    return [item for item in permissions if not _is_home_permission(item)]


def _build_permission_tree(permissions):
    system_nodes = OrderedDict()

    for item in permissions:
        permission_code = str(item.permission_code or '').strip()
        if not permission_code:
            continue

        segments = [segment.strip() for segment in permission_code.split(':') if segment.strip()]
        if len(segments) < 3:
            continue

        system_code = segments[0]
        module_code = segments[1]
        menu_code = segments[2]
        action_code = ':'.join(segments[3:]) if len(segments) > 3 else ''

        system_key = system_code.lower()
        system_node = system_nodes.setdefault(
            system_key,
            {
                'id': f'system:{system_key}',
                'label': _system_label(system_code),
                'code': system_code,
                'children': [],
                '_modules': OrderedDict(),
            },
        )

        module_key = f'{system_key}:{module_code.lower()}'
        module_node = system_node['_modules'].setdefault(
            module_key,
            {
                'id': f'module:{module_key}',
                'label': _safe_label(module_code),
                'code': module_code,
                'children': [],
                '_menus': OrderedDict(),
            },
        )

        menu_key = f'{module_key}:{menu_code.lower()}'
        menu_node = module_node['_menus'].setdefault(
            menu_key,
            {
                'id': f'menu:{menu_key}',
                'label': _safe_label(menu_code),
                'code': f'{system_code}:{module_code}:{menu_code}',
                'children': [],
                '_action_codes': set(),
            },
        )

        if not action_code:
            leaf = {
                'id': item.id,
                'label': item.permission_name or _safe_label(menu_code),
                'permission_code': permission_code,
                'permission_name': item.permission_name,
                'description': item.description,
                'children': [],
            }
            menu_node['children'] = [leaf]
            continue

        if action_code in menu_node['_action_codes']:
            continue

        menu_node['_action_codes'].add(action_code)
        menu_node['children'].append(
            {
                'id': item.id,
                'label': item.permission_name or _safe_label(action_code),
                'permission_code': permission_code,
                'permission_name': item.permission_name,
                'description': item.description,
                'action': action_code,
                'children': [],
            }
        )

    tree = []
    for system_node in system_nodes.values():
        modules = []
        for module_node in system_node['_modules'].values():
            menus = []
            for menu_node in module_node['_menus'].values():
                menu_node.pop('_action_codes', None)
                menus.append(menu_node)
            module_node.pop('_menus', None)
            module_node['children'] = menus
            modules.append(module_node)
        system_node.pop('_modules', None)
        system_node['children'] = modules
        tree.append(system_node)

    return tree


def _normalize_permission_ids(permission_ids):
    if not isinstance(permission_ids, list):
        raise InvalidUsageError('permission_ids 必须是数组')

    normalized_permission_ids = []
    seen = set()
    for item in permission_ids:
        if not isinstance(item, str) or not item.strip():
            raise InvalidUsageError('permission_ids 中的每一项都必须是非空字符串')
        pid = item.strip()
        if pid not in seen:
            seen.add(pid)
            normalized_permission_ids.append(pid)

    return normalized_permission_ids


def _validate_role_permission_ids(role_id, normalized_permission_ids):
    role_exists = Role.query.with_entities(Role.id).filter(Role.id == role_id).first()
    if not role_exists:
        raise ApiException(message='角色不存在', status_code=404)

    if not normalized_permission_ids:
        return

    permission_rows = Permission.query.filter(Permission.id.in_(normalized_permission_ids)).all()
    existed_permission_ids = {row.id for row in permission_rows}
    missing_permission_ids = sorted(set(normalized_permission_ids) - existed_permission_ids)
    if missing_permission_ids:
        raise InvalidUsageError(f'权限不存在: {", ".join(missing_permission_ids)}')
    if any(_is_home_permission(row) for row in permission_rows):
        raise InvalidUsageError('首页为公共路由，不允许录入或分配权限')


def list_permissions_tree():
    valid_permissions = _get_all_non_home_permissions()
    return _build_permission_tree(valid_permissions)


def list_current_user_permissions(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise ApiException(message='用户不存在', status_code=404)

    # TODO(RBAC): 在后续动态路由/菜单权限体系中，若当前登录账号为 superadmin，
    # 直接下发系统全量权限并忽略权限映射表，确保内置超级管理员始终具备兜底控制权。
    if str(user.account or '').strip().lower() == 'superadmin':
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    if _is_admin_account(user.account):
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    if '管理员' in str(user.full_name or ''):
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    if user.role and '管理员' in str(user.role.role_name or ''):
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    role_id = user.role_id
    if not role_id:
        return []

    if _is_admin_role_id(role_id):
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    rows = (
        db.session.query(Permission)
        .join(RoleMappingPermission, RoleMappingPermission.permission_id == Permission.id)
        .filter(RoleMappingPermission.role_id == role_id)
        .order_by(Permission.permission_code.asc())
        .all()
    )
    return [_permission_to_dict(item) for item in rows if not _is_home_permission(item)]


def list_role_permission_ids(role_id):
    if _is_admin_role_id(role_id):
        permission_ids = [item.id for item in _get_all_non_home_permissions()]
        return {
            'role_id': role_id,
            'permission_ids': permission_ids,
        }

    permission_rows = (
        db.session.query(Permission.id, Permission.permission_code, Permission.permission_name)
        .join(RoleMappingPermission, RoleMappingPermission.permission_id == Permission.id)
        .filter(RoleMappingPermission.role_id == role_id)
        .order_by(Permission.permission_code.asc())
        .all()
    )

    permission_ids = [item.id for item in permission_rows if not _is_home_permission(item)]
    return {
        'role_id': role_id,
        'permission_ids': permission_ids,
    }


def list_role_permissions(role_id):
    if _is_admin_role_id(role_id):
        return [_permission_to_dict(item) for item in _get_all_non_home_permissions()]

    rows = (
        db.session.query(Permission)
        .join(RoleMappingPermission, RoleMappingPermission.permission_id == Permission.id)
        .filter(RoleMappingPermission.role_id == role_id)
        .order_by(Permission.permission_code.asc())
        .all()
    )
    return [_permission_to_dict(item) for item in rows if not _is_home_permission(item)]


@transactional(db_error_message='分配权限失败，数据库事务已回滚')
def replace_role_permissions(role_id, permission_ids):
    normalized_permission_ids = _normalize_permission_ids(permission_ids)
    _validate_role_permission_ids(role_id, normalized_permission_ids)

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

    return {
        'role_id': role_id,
        'permission_ids': normalized_permission_ids,
    }


@transactional(db_error_message='分配权限失败，数据库事务已回滚')
def add_role_permissions(role_id, permission_ids):
    normalized_permission_ids = _normalize_permission_ids(permission_ids)
    _validate_role_permission_ids(role_id, normalized_permission_ids)

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

    return {
        'role_id': role_id,
        'permission_ids': normalized_permission_ids,
    }


@transactional(db_error_message='分配权限失败，数据库事务已回滚')
def remove_role_permissions(role_id, permission_ids):
    normalized_permission_ids = _normalize_permission_ids(permission_ids)
    _validate_role_permission_ids(role_id, normalized_permission_ids)

    if normalized_permission_ids:
        RoleMappingPermission.query.filter(
            RoleMappingPermission.role_id == role_id,
            RoleMappingPermission.permission_id.in_(normalized_permission_ids),
        ).delete(synchronize_session=False)

    return {
        'role_id': role_id,
        'permission_ids': normalized_permission_ids,
    }
