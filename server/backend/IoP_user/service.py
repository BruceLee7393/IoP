from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import db
from backend.IoP_role.model import Role
from backend.IoP_user.model import User


ALLOWED_STATUS = {'active', 'disabled'}
ALLOWED_GENDER = {'woman', 'man', 'none', 'others'}
SUPERADMIN_ACCOUNT = 'superadmin'


def user_to_dict(user):
    return {
        'id': user.id,
        'account': user.account,
        'full_name': user.full_name,
        'contact_info': user.contact_info,
        'address': user.address,
        'gender': user.gender,
        'status': user.status,
        'role_id': user.role_id,
        'role': {
            'id': user.role.id,
            'role_name': user.role.role_name,
        }
        if user.role
        else None,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None,
    }


def _normalize_role_id(role_id):
    if isinstance(role_id, str):
        role_id = role_id.strip() or None
    return role_id


def _require_role_if_provided(role_id):
    if not role_id:
        return None

    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        raise ApiException(message='角色不存在', status_code=404)
    return role


def _get_user_or_404(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise ApiException(message='用户不存在', status_code=404)
    return user


def _is_superadmin_user(user):
    account = str(getattr(user, 'account', '') or '').strip().lower()
    return account == SUPERADMIN_ACCOUNT


def _guard_superadmin_mutation(user):
    if _is_superadmin_user(user):
        raise InvalidUsageError('系统内置超级管理员，禁止修改基本信息与状态')


def _guard_superadmin_delete(user):
    if _is_superadmin_user(user):
        raise InvalidUsageError('系统内置超级管理员，禁止删除')


def _raise_integrity_error(exc):
    err_text = str(getattr(exc, 'orig', exc)).lower()
    if 'account' in err_text or 'iop_users.account' in err_text:
        raise InvalidUsageError('用户账号已存在') from exc
    if 'role_id' in err_text or 'foreign key' in err_text:
        raise InvalidUsageError('角色不存在或角色ID无效') from exc
    raise InvalidUsageError('用户数据违反完整性约束') from exc


def list_users(query_args):
    page = query_args.get('page', 1, type=int)
    per_page = query_args.get('per_page', 10, type=int)
    sort_by = str(query_args.get('sort_by', 'created_at') or 'created_at').strip()
    sort_order = str(query_args.get('sort_order', 'desc') or 'desc').strip()

    account = query_args.get('account', type=str)
    full_name = query_args.get('full_name', type=str)
    status = query_args.get('status', type=str)
    role_id = query_args.get('role_id', type=str)

    if page <= 0 or per_page <= 0:
        raise InvalidUsageError('page 和 per_page 必须大于 0')
    if status and status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 active 或 disabled')

    query = User.query.options(joinedload(User.role))

    if account:
        query = query.filter(User.account.like(f'{account}%'))
    if full_name:
        query = query.filter(User.full_name.like(f'%{full_name}%'))
    if status:
        query = query.filter(User.status == status)
    if role_id:
        query = query.filter(User.role_id == role_id)

    sort_map = {
        'account': User.account,
        'full_name': User.full_name,
        'status': User.status,
        'created_at': User.created_at,
        'updated_at': User.updated_at,
    }
    sort_col = sort_map.get(sort_by, User.created_at)
    query = query.order_by(sort_col.asc() if sort_order == 'asc' else sort_col.desc())

    paged = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [user_to_dict(item) for item in paged.items],
        'pagination': {
            'total': paged.total,
            'pages': paged.pages,
            'page': paged.page,
            'per_page': paged.per_page,
        },
    }


def get_user_detail(user_id):
    user = User.query.options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        raise ApiException(message='用户不存在', status_code=404)
    return user_to_dict(user)


@transactional(
    integrity_error_message='用户账号已存在',
    db_error_message='创建用户失败，发生未知错误。',
)
def create_user(payload):
    account = str(payload.get('account', '')).strip()
    password = str(payload.get('password', '')).strip()
    full_name = payload.get('full_name')
    role_id = _normalize_role_id(payload.get('role_id'))
    status = str(payload.get('status', 'active')).strip() or 'active'
    contact_info = payload.get('contact_info')
    address = payload.get('address')
    extra_data = payload.get('extra_data')

    if not account or not password:
        raise InvalidUsageError('account 和 password 是必填项')

    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 active 或 disabled')
    _require_role_if_provided(role_id)

    existed = User.query.filter(User.account == account).first()
    if existed:
        raise InvalidUsageError('用户账号已存在')

    user = User(
        account=account,
        full_name=full_name,
        contact_info=contact_info,
        address=address,
        gender='none',
        status=status,
        role_id=role_id,
        extra_data=extra_data,
    )
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.flush()
    except IntegrityError as exc:
        raise InvalidUsageError('用户账号已存在') from exc

    return None


@transactional(
    integrity_error_message='用户数据违反完整性约束',
    db_error_message='更新用户失败，发生未知错误。',
)
def update_user(user_id, payload):
    user = _get_user_or_404(user_id)
    _guard_superadmin_mutation(user)

    if 'account' in payload:
        account = str(payload.get('account', '')).strip()
        if not account:
            raise InvalidUsageError('account 不能为空')
        duplicated = User.query.filter(User.account == account, User.id != user.id).first()
        if duplicated:
            raise InvalidUsageError('用户账号已存在')
        user.account = account

    if 'full_name' in payload:
        user.full_name = payload.get('full_name')

    if 'contact_info' in payload:
        user.contact_info = payload.get('contact_info')

    if 'address' in payload:
        user.address = payload.get('address')

    if 'gender' in payload:
        gender = str(payload.get('gender', '')).strip()
        if gender not in ALLOWED_GENDER:
            raise InvalidUsageError('gender 仅支持 woman/man/none/others')
        user.gender = gender

    if 'status' in payload:
        status = str(payload.get('status', '')).strip()
        if status not in ALLOWED_STATUS:
            raise InvalidUsageError('status 仅支持 active 或 disabled')
        user.status = status

    if 'role_id' in payload:
        role_id = _normalize_role_id(payload.get('role_id'))
        _require_role_if_provided(role_id)
        user.role_id = role_id

    if 'extra_data' in payload:
        user.extra_data = payload.get('extra_data')

    if 'password' in payload:
        new_password = str(payload.get('password', '')).strip()
        if not new_password:
            raise InvalidUsageError('password 不能为空')
        user.set_password(new_password)

    try:
        db.session.flush()
    except IntegrityError as exc:
        _raise_integrity_error(exc)

    refreshed = User.query.options(joinedload(User.role)).filter(User.id == user.id).first()
    return user_to_dict(refreshed)


@transactional(db_error_message='状态更新失败，发生未知错误。')
def toggle_user_status(user_id, status):
    user = _get_user_or_404(user_id)
    _guard_superadmin_mutation(user)
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 active 或 disabled')

    user.status = status
    refreshed = User.query.options(joinedload(User.role)).filter(User.id == user.id).first()
    return user_to_dict(refreshed)


@transactional(db_error_message='重置密码失败，发生未知错误。')
def reset_user_password(user_id, password):
    user = _get_user_or_404(user_id)
    new_password = str(password or '').strip()
    if not new_password:
        raise InvalidUsageError('password 是必填项')

    user.set_password(new_password)
    return {'updated': True, 'user_id': user.id}


@transactional(db_error_message='删除用户失败，发生未知错误。')
def delete_user(user_id):
    user = _get_user_or_404(user_id)
    _guard_superadmin_delete(user)
    db.session.delete(user)
    return {'deleted': True, 'user_id': user_id}
