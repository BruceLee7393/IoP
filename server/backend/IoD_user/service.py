from datetime import datetime

from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import bcrypt, db
from backend.IoD_department.model import IodDepartment
from backend.IoD_mapping.model import IodUserDepartment
from backend.IoD_role.model import IodRole
from backend.IoD_user.model import IodUser


ALLOWED_STATUS = {0, 1}
SUPERADMIN_USER_ID = 'superadmin'


def _format_datetime(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')


def _parse_datetime_filter(raw_value, field_name):
    if raw_value is None:
        return None

    value = str(raw_value).strip()
    if not value:
        return None

    normalized = value.replace('T', ' ')
    parse_formats = (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    )

    for fmt in parse_formats:
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue

    raise InvalidUsageError(f'{field_name} 时间格式不正确')


def _normalize_id_list(value, field_name):
    if value is None:
        return []
    if not isinstance(value, list):
        raise InvalidUsageError(f'{field_name} 必须是数组')

    normalized = []
    seen = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise InvalidUsageError(f'{field_name} 中的每一项都必须是非空字符串')
        item_id = item.strip()
        if item_id not in seen:
            seen.add(item_id)
            normalized.append(item_id)
    return normalized


def _validate_role_id(role_id):
    if role_id is None:
        return None
    if not isinstance(role_id, str) or not role_id.strip():
        raise InvalidUsageError('role_id 必须是非空字符串')

    normalized_role_id = role_id.strip()
    role_exists = (
        IodRole.query.with_entities(IodRole.id)
        .filter(IodRole.id == normalized_role_id)
        .first()
    )
    if not role_exists:
        raise ApiException(message='角色不存在', status_code=404)
    return normalized_role_id


def _validate_department_ids(department_ids):
    if not department_ids:
        return []

    rows = IodDepartment.query.with_entities(IodDepartment.id).filter(IodDepartment.id.in_(department_ids)).all()
    existed_ids = {item[0] for item in rows}
    missing = sorted(set(department_ids) - existed_ids)
    if missing:
        raise InvalidUsageError(f'部门不存在: {", ".join(missing)}')
    return department_ids


def _get_user_or_404(user_id):
    user = IodUser.query.filter(IodUser.id == user_id).first()
    if not user:
        raise ApiException(message='用户不存在', status_code=404)
    return user


def _is_superadmin_user(user):
    account = str(getattr(user, 'user_id', '') or '').strip().lower()
    return account == SUPERADMIN_USER_ID


def _guard_superadmin_mutation(user):
    if _is_superadmin_user(user):
        raise InvalidUsageError('系统内置超级管理员，禁止修改基本信息与状态')


def _guard_superadmin_delete(user):
    if _is_superadmin_user(user):
        raise InvalidUsageError('系统内置超级管理员，禁止删除')


def _get_user_department_map(user_ids):
    if not user_ids:
        return {}

    rows = (
        db.session.query(IodUserDepartment.user_id, IodDepartment.id, IodDepartment.dept_name)
        .join(IodDepartment, IodDepartment.id == IodUserDepartment.dept_id)
        .filter(IodUserDepartment.user_id.in_(user_ids))
        .all()
    )

    result = {user_id: [] for user_id in user_ids}
    for user_id, dept_id, dept_name in rows:
        result.setdefault(user_id, []).append({'id': dept_id, 'dept_name': dept_name})
    return result


def _user_to_dict(user, departments=None):
    departments = departments or []
    return {
        'id': user.id,
        'user_id': user.user_id,
        'user_name': user.user_name,
        'role_id': user.role_id,
        'role_name': user.role.role_name if user.role else None,
        'status': int(user.status),
        'nfc_uid': user.nfc_uid,
        'creditor_name': user.creditor_name,
        'bic': user.bic,
        'iban': user.iban,
        'department_ids': [item['id'] for item in departments],
        'departments': departments,
        'created_at': _format_datetime(user.created_at),
        'updated_at': _format_datetime(user.updated_at),
    }


def list_users(query_args):
    page = query_args.get('page', 1, type=int)
    per_page = query_args.get('per_page', 10, type=int)
    user_id = query_args.get('user_id', type=str)
    user_name = query_args.get('user_name', type=str)
    creditor_name = query_args.get('creditor_name', type=str)
    bic = query_args.get('bic', type=str)
    iban = query_args.get('iban', type=str)
    role_id = query_args.get('role_id', type=str)
    status = query_args.get('status', type=int)
    created_at_start = _parse_datetime_filter(query_args.get('created_at_start', type=str), 'created_at_start')
    created_at_end = _parse_datetime_filter(query_args.get('created_at_end', type=str), 'created_at_end')
    sort_by = str(query_args.get('sort_by', 'created_at') or 'created_at').strip()
    sort_order = str(query_args.get('sort_order', 'desc') or 'desc').strip()

    if page <= 0 or per_page <= 0:
        raise InvalidUsageError('page 和 per_page 必须大于 0')
    if status is not None and status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')
    if created_at_start and created_at_end and created_at_start > created_at_end:
        raise InvalidUsageError('created_at_start 不能晚于 created_at_end')

    query = IodUser.query
    if user_id:
        query = query.filter(IodUser.user_id.like(f'%{user_id}%'))
    if user_name:
        query = query.filter(IodUser.user_name.like(f'%{user_name}%'))
    if creditor_name:
        query = query.filter(IodUser.creditor_name.like(f'%{creditor_name}%'))
    if bic:
        query = query.filter(IodUser.bic.like(f'%{bic}%'))
    if iban:
        query = query.filter(IodUser.iban.like(f'%{iban}%'))
    if role_id:
        query = query.filter(IodUser.role_id == role_id)
    if status is not None:
        query = query.filter(IodUser.status == status)
    if created_at_start:
        query = query.filter(IodUser.created_at >= created_at_start)
    if created_at_end:
        query = query.filter(IodUser.created_at <= created_at_end)

    sort_map = {
        'user_id': IodUser.user_id,
        'user_name': IodUser.user_name,
        'status': IodUser.status,
        'created_at': IodUser.created_at,
        'updated_at': IodUser.updated_at,
    }
    sort_col = sort_map.get(sort_by, IodUser.created_at)
    query = query.order_by(sort_col.asc() if sort_order == 'asc' else sort_col.desc())

    paged = query.paginate(page=page, per_page=per_page, error_out=False)
    user_ids = [item.id for item in paged.items]
    user_dept_map = _get_user_department_map(user_ids)

    return {
        'items': [_user_to_dict(item, user_dept_map.get(item.id, [])) for item in paged.items],
        'pagination': {
            'total': paged.total,
            'pages': paged.pages,
            'page': paged.page,
            'per_page': paged.per_page,
        },
    }


def get_user_detail(user_id):
    user = _get_user_or_404(user_id)
    user_dept_map = _get_user_department_map([user.id])
    return _user_to_dict(user, user_dept_map.get(user.id, []))


@transactional(
    integrity_error_message='用户账号或NFC卡已存在',
    db_error_message='创建用户失败，数据库事务已回滚',
)
def create_user(payload):
    account = str(payload.get('user_id', '')).strip()
    password = str(payload.get('password', '')).strip()
    user_name = payload.get('user_name')
    role_id = _validate_role_id(payload.get('role_id'))
    status = payload.get('status', 1)
    nfc_uid = payload.get('nfc_uid')
    creditor_name = payload.get('creditor_name')
    bic = payload.get('bic')
    iban = payload.get('iban')
    department_ids = _validate_department_ids(_normalize_id_list(payload.get('department_ids'), 'department_ids'))

    if not account or not password:
        raise InvalidUsageError('user_id 和 password 是必填项')
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')

    existed_account = IodUser.query.with_entities(IodUser.id).filter(IodUser.user_id == account).first()
    if existed_account:
        raise InvalidUsageError('用户账号已存在')

    user = IodUser(
        user_id=account,
        user_name=user_name,
        role_id=role_id,
        status=status,
        nfc_uid=nfc_uid,
        creditor_name=creditor_name,
        bic=bic,
        iban=iban,
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
    )
    db.session.add(user)
    db.session.flush()

    if department_ids:
        db.session.add_all(
            [
                IodUserDepartment(user_id=user.id, dept_id=dept_id)
                for dept_id in department_ids
            ]
        )

    user_dept_map = _get_user_department_map([user.id])
    return _user_to_dict(user, user_dept_map.get(user.id, []))


@transactional(
    integrity_error_message='用户账号或NFC卡已存在',
    db_error_message='更新用户失败，数据库事务已回滚',
)
def update_user(user_id, payload):
    user = _get_user_or_404(user_id)
    _guard_superadmin_mutation(user)

    if 'user_id' in payload:
        account = str(payload.get('user_id', '')).strip()
        if not account:
            raise InvalidUsageError('user_id 不能为空')
        duplicated = (
            IodUser.query.with_entities(IodUser.id)
            .filter(IodUser.user_id == account, IodUser.id != user.id)
            .first()
        )
        if duplicated:
            raise InvalidUsageError('用户账号已存在')
        user.user_id = account

    if 'user_name' in payload:
        user.user_name = payload.get('user_name')

    if 'password' in payload:
        password = str(payload.get('password') or '').strip()
        if not password:
            raise InvalidUsageError('password 不能为空')
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    if 'role_id' in payload:
        user.role_id = _validate_role_id(payload.get('role_id'))

    if 'status' in payload:
        status = payload.get('status')
        if status not in ALLOWED_STATUS:
            raise InvalidUsageError('status 仅支持 0 或 1')
        user.status = status

    if 'nfc_uid' in payload:
        user.nfc_uid = payload.get('nfc_uid')

    if 'creditor_name' in payload:
        user.creditor_name = payload.get('creditor_name')

    if 'bic' in payload:
        user.bic = payload.get('bic')

    if 'iban' in payload:
        user.iban = payload.get('iban')

    if 'department_ids' in payload:
        department_ids = _validate_department_ids(
            _normalize_id_list(payload.get('department_ids'), 'department_ids')
        )
        IodUserDepartment.query.filter(IodUserDepartment.user_id == user.id).delete(synchronize_session=False)
        if department_ids:
            db.session.add_all(
                [
                    IodUserDepartment(user_id=user.id, dept_id=dept_id)
                    for dept_id in department_ids
                ]
            )

    db.session.flush()
    user_dept_map = _get_user_department_map([user.id])
    return _user_to_dict(user, user_dept_map.get(user.id, []))


@transactional(db_error_message='更新用户状态失败，数据库事务已回滚')
def change_user_status(user_id, status):
    user = _get_user_or_404(user_id)
    _guard_superadmin_mutation(user)
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')
    user.status = status
    user_dept_map = _get_user_department_map([user.id])
    return _user_to_dict(user, user_dept_map.get(user.id, []))


@transactional(db_error_message='重置密码失败，数据库事务已回滚')
def reset_user_password(user_id, new_password):
    user = _get_user_or_404(user_id)
    password = str(new_password or '').strip()
    if not password:
        raise InvalidUsageError('password 是必填项')

    user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return {'updated': True, 'id': user.id}


@transactional(db_error_message='删除用户失败，数据库事务已回滚')
def delete_user(user_id):
    user = _get_user_or_404(user_id)
    _guard_superadmin_delete(user)
    IodUserDepartment.query.filter(IodUserDepartment.user_id == user.id).delete(synchronize_session=False)
    db.session.delete(user)
    return {'deleted': True, 'id': user.id}
