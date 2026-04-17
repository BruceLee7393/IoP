from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import db
from backend.IoD_role.model import IodRole
from backend.IoD_user.model import IodUser


ALLOWED_STATUS = {0, 1}


def _format_datetime(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')


def _role_to_dict(role):
    return {
        'id': role.id,
        'role_name': role.role_name,
        'description': role.description,
        'is_preset': 1 if role.is_preset else 0,
        'status': int(role.status),
        'created_at': _format_datetime(role.created_at),
        'updated_at': _format_datetime(role.updated_at),
    }


def _get_role_or_404(role_id):
    role = IodRole.query.filter(IodRole.id == role_id).first()
    if not role:
        raise ApiException(message='角色不存在', status_code=404)
    return role


def list_roles(query_args):
    page = query_args.get('page', 1, type=int)
    per_page = query_args.get('per_page', 10, type=int)
    role_name = query_args.get('role_name', type=str)
    status = query_args.get('status', type=int)

    if page <= 0 or per_page <= 0:
        raise InvalidUsageError('page 和 per_page 必须大于 0')
    if status is not None and status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')

    query = IodRole.query
    if role_name:
        query = query.filter(IodRole.role_name.like(f'%{role_name}%'))
    if status is not None:
        query = query.filter(IodRole.status == status)

    query = query.order_by(IodRole.created_at.desc())
    paged = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [_role_to_dict(item) for item in paged.items],
        'pagination': {
            'total': paged.total,
            'pages': paged.pages,
            'page': paged.page,
            'per_page': paged.per_page,
        },
    }


def get_role_detail(role_id):
    role = _get_role_or_404(role_id)
    return _role_to_dict(role)


@transactional(
    integrity_error_message='角色名称已存在',
    db_error_message='创建角色失败，数据库事务已回滚',
)
def create_role(payload):
    role_name = str(payload.get('role_name', '')).strip()
    description = payload.get('description')
    status = payload.get('status', 1)

    if not role_name:
        raise InvalidUsageError('role_name 是必填项')
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')

    existed = IodRole.query.with_entities(IodRole.id).filter(IodRole.role_name == role_name).first()
    if existed:
        raise InvalidUsageError('角色名称已存在')

    role = IodRole(role_name=role_name, description=description, status=status, is_preset=False)
    db.session.add(role)
    db.session.flush()
    return _role_to_dict(role)


@transactional(
    integrity_error_message='角色名称已存在',
    db_error_message='更新角色失败，数据库事务已回滚',
)
def update_role(role_id, payload):
    role = _get_role_or_404(role_id)

    if 'role_name' in payload:
        role_name = str(payload.get('role_name', '')).strip()
        if not role_name:
            raise InvalidUsageError('role_name 不能为空')
        duplicated = (
            IodRole.query.with_entities(IodRole.id)
            .filter(IodRole.role_name == role_name, IodRole.id != role.id)
            .first()
        )
        if duplicated:
            raise InvalidUsageError('角色名称已存在')
        role.role_name = role_name

    if 'description' in payload:
        role.description = payload.get('description')

    if 'status' in payload:
        status = payload.get('status')
        if status not in ALLOWED_STATUS:
            raise InvalidUsageError('status 仅支持 0 或 1')
        role.status = status

    db.session.flush()
    return _role_to_dict(role)


@transactional(db_error_message='更新角色状态失败，数据库事务已回滚')
def change_role_status(role_id, status):
    role = _get_role_or_404(role_id)
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError('status 仅支持 0 或 1')
    role.status = status
    return _role_to_dict(role)


@transactional(db_error_message='删除角色失败，数据库事务已回滚')
def delete_role(role_id):
    role = _get_role_or_404(role_id)

    if bool(role.is_preset):
        raise InvalidUsageError('系统预设角色不允许删除')

    related_user_count = (
        IodUser.query.with_entities(IodUser.id)
        .filter(IodUser.role_id == role_id)
        .count()
    )
    if related_user_count > 0:
        raise InvalidUsageError('该角色下仍有关联用户，无法删除')

    db.session.delete(role)
    return {'deleted': True, 'id': role.id}
