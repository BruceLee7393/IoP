from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from backend.extensions import db
from backend.IoP_role.model import Role
from backend.IoP_user.model import User

IoP_user_bp = Blueprint('IoP_user', __name__, url_prefix='/api/iop/user')


def _success(data, message='操作成功', status=200):
    return jsonify({'code': 0, 'message': message, 'data': data}), status


def _error(message, status):
    return jsonify({'code': status, 'message': message, 'data': None}), status


def _user_to_dict(user):
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


def _get_role_or_error(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        return None, _error('角色不存在', 404)
    return role, None


def _create_user_impl():
    payload = request.get_json(silent=True) or {}

    account = str(payload.get('account', '')).strip()
    password = str(payload.get('password', '')).strip()
    full_name = payload.get('full_name')
    role_id = payload.get('role_id')
    if isinstance(role_id, str):
        role_id = role_id.strip() or None
    status = str(payload.get('status', 'active')).strip() or 'active'
    contact_info = payload.get('contact_info')
    address = payload.get('address')
    extra_data = payload.get('extra_data')

    if not account or not password:
        return _error('account 和 password 是必填项', 400)

    if status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

    existed = User.query.filter(User.account == account).first()
    if existed:
        return _error('用户账号已存在', 400)

    if role_id:
        _, role_error = _get_role_or_error(role_id)
        if role_error:
            return role_error

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

    # Password must always be stored as bcrypt hash.
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error('用户账号已存在', 400)
    except Exception:
        db.session.rollback()
        return _error('创建用户失败，发生未知错误。', 500)

    return _success(None, message='新增用户成功', status=200)


@IoP_user_bp.route('', methods=['POST'])
def create_user():
    return _create_user_impl()


@IoP_user_bp.route('/register', methods=['POST'])
def create_user_register():
    return _create_user_impl()


@IoP_user_bp.route('', methods=['GET'])
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)

    account = request.args.get('account', type=str)
    full_name = request.args.get('full_name', type=str)
    status = request.args.get('status', type=str)
    role_id = request.args.get('role_id', type=str)

    if page <= 0 or per_page <= 0:
        return _error('page 和 per_page 必须大于 0', 400)
    if status and status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

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

    return _success(
        {
            'items': [_user_to_dict(item) for item in paged.items],
            'pagination': {
                'total': paged.total,
                'pages': paged.pages,
                'page': paged.page,
                'per_page': paged.per_page,
            },
        },
        message='获取用户列表成功',
    )


@IoP_user_bp.route('/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)
    return _success(_user_to_dict(user), message='获取用户详情成功')


@IoP_user_bp.route('/<string:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)

    payload = request.get_json(silent=True) or {}

    if 'account' in payload:
        account = str(payload.get('account', '')).strip()
        if not account:
            return _error('account 不能为空', 400)
        duplicated = User.query.filter(User.account == account, User.id != user.id).first()
        if duplicated:
            return _error('用户账号已存在', 400)
        user.account = account

    if 'full_name' in payload:
        user.full_name = payload.get('full_name')

    if 'contact_info' in payload:
        user.contact_info = payload.get('contact_info')

    if 'address' in payload:
        user.address = payload.get('address')

    if 'gender' in payload:
        gender = str(payload.get('gender', '')).strip()
        if gender not in {'woman', 'man', 'none', 'others'}:
            return _error('gender 仅支持 woman/man/none/others', 400)
        user.gender = gender

    if 'status' in payload:
        status = str(payload.get('status', '')).strip()
        if status not in {'active', 'disabled'}:
            return _error('status 仅支持 active 或 disabled', 400)
        user.status = status

    if 'role_id' in payload:
        role_id = payload.get('role_id')
        if isinstance(role_id, str):
            role_id = role_id.strip() or None
        if role_id:
            _, role_error = _get_role_or_error(role_id)
            if role_error:
                return role_error
        user.role_id = role_id

    if 'extra_data' in payload:
        user.extra_data = payload.get('extra_data')

    if 'password' in payload:
        new_password = str(payload.get('password', '')).strip()
        if not new_password:
            return _error('password 不能为空', 400)
        user.set_password(new_password)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        err_text = str(getattr(exc, 'orig', exc)).lower()
        if 'account' in err_text or 'iop_users.account' in err_text:
            return _error('用户账号已存在', 400)
        if 'role_id' in err_text or 'foreign key' in err_text:
            return _error('角色不存在或角色ID无效', 400)
        return _error('用户数据违反完整性约束', 400)
    except Exception:
        db.session.rollback()
        return _error('更新用户失败，发生未知错误。', 500)

    user = User.query.options(joinedload(User.role)).filter(User.id == user.id).first()
    return _success(_user_to_dict(user), message='更新用户成功')


@IoP_user_bp.route('/<string:user_id>/status', methods=['PATCH'])
def toggle_user_status(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)

    payload = request.get_json(silent=True) or {}
    status = str(payload.get('status', '')).strip()
    if status not in {'active', 'disabled'}:
        return _error('status 仅支持 active 或 disabled', 400)

    user.status = status
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('状态更新失败，发生未知错误。', 500)

    user = User.query.options(joinedload(User.role)).filter(User.id == user.id).first()
    return _success(_user_to_dict(user), message='更新用户状态成功')


@IoP_user_bp.route('/<string:user_id>/reset-password', methods=['PATCH'])
def reset_password(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)

    payload = request.get_json(silent=True) or {}
    new_password = str(payload.get('password', '')).strip()
    if not new_password:
        return _error('password 是必填项', 400)

    # Password reset must always use bcrypt hashing.
    user.set_password(new_password)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('重置密码失败，发生未知错误。', 500)

    return _success({'updated': True, 'user_id': user.id}, message='用户密码重置成功')


@IoP_user_bp.route('/<string:user_id>/password-reset', methods=['POST'])
def reset_password_compat(user_id):
    payload = request.get_json(silent=True) or {}
    if 'newPassword' in payload and 'password' not in payload:
        payload = {'password': payload.get('newPassword')}

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)

    new_password = str(payload.get('password', '')).strip()
    if not new_password:
        return _error('password 是必填项', 400)

    user.set_password(new_password)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('重置密码失败，发生未知错误。', 500)

    return _success({'updated': True, 'user_id': user.id}, message='用户密码重置成功')


@IoP_user_bp.route('/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return _error('用户不存在', 404)

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return _error('删除用户失败，发生未知错误。', 500)

    return _success({'deleted': True, 'user_id': user_id}, message='删除用户成功')
