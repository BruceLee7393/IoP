from sqlalchemy.exc import IntegrityError

from backend.common.datetime_utils import format_datetime_to_utc_z
from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import db
from backend.IoP_mapping.model import RoleMappingPermission
from backend.IoP_role.model import Role
from backend.IoP_user.model import User


ALLOWED_STATUS = {"active", "disabled"}


def role_to_dict(role):
    return {
        "id": role.id,
        "role_code": role.role_code,
        "role_name": role.role_name,
        "description": role.description,
        "status": role.status,
        "extra_data": role.extra_data,
        "created_at": format_datetime_to_utc_z(role.created_at),
        "updated_at": format_datetime_to_utc_z(role.updated_at),
    }


def _get_role_or_404(role_id):
    role = Role.query.filter(Role.id == role_id).first()
    if not role:
        raise ApiException(message="角色不存在", status_code=404)
    return role


def list_roles(query_args):
    page = query_args.get("page", 1, type=int)
    per_page = query_args.get("per_page", 10, type=int)
    sort_by = query_args.get("sort_by", "created_at", type=str)
    sort_order = query_args.get("sort_order", "desc", type=str)

    role_code = query_args.get("role_code", type=str)
    role_name = query_args.get("role_name", type=str)
    status = query_args.get("status", type=str)

    if page <= 0 or per_page <= 0:
        raise InvalidUsageError("page 和 per_page 必须大于 0")
    if status and status not in ALLOWED_STATUS:
        raise InvalidUsageError("status 仅支持 active 或 disabled")

    query = Role.query

    if role_code:
        query = query.filter(Role.role_code.like(f"{role_code}%"))
    if role_name:
        query = query.filter(Role.role_name.like(f"%{role_name}%"))
    if status:
        query = query.filter(Role.status == status)

    sort_map = {
        "role_code": Role.role_code,
        "role_name": Role.role_name,
        "status": Role.status,
        "created_at": Role.created_at,
        "updated_at": Role.updated_at,
    }
    sort_col = sort_map.get(sort_by, Role.created_at)
    query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())

    paged = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": [role_to_dict(item) for item in paged.items],
        "pagination": {
            "total": paged.total,
            "pages": paged.pages,
            "page": paged.page,
            "per_page": paged.per_page,
        },
    }


def get_role_detail(role_id):
    role = _get_role_or_404(role_id)
    return role_to_dict(role)


@transactional(
    integrity_error_message="角色编码已存在",
    db_error_message="创建角色失败，发生未知错误。",
)
def create_role(payload):
    role_code = str(payload.get("role_code", "")).strip()
    role_name = str(payload.get("role_name", "")).strip()
    description = payload.get("description")
    status = str(payload.get("status", "active")).strip() or "active"
    extra_data = payload.get("extra_data")

    if not role_code or not role_name:
        raise InvalidUsageError("role_code 和 role_name 是必填项")
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError("status 仅支持 active 或 disabled")

    existed = Role.query.filter(Role.role_code == role_code).first()
    if existed:
        raise ApiException(message="角色编码已存在", status_code=409)

    role = Role(
        role_code=role_code,
        role_name=role_name,
        description=description,
        status=status,
        extra_data=extra_data,
    )
    db.session.add(role)

    try:
        db.session.flush()
    except IntegrityError as exc:
        raise ApiException(message="角色编码已存在", status_code=409) from exc

    return role_to_dict(role)


@transactional(
    integrity_error_message="角色编码已存在",
    db_error_message="更新角色失败，发生未知错误。",
)
def update_role(role_id, payload):
    role = _get_role_or_404(role_id)

    if "role_code" in payload:
        role_code = str(payload.get("role_code", "")).strip()
        if not role_code:
            raise InvalidUsageError("role_code 不能为空")
        duplicated = Role.query.filter(
            Role.role_code == role_code, Role.id != role.id
        ).first()
        if duplicated:
            raise ApiException(message="角色编码已存在", status_code=409)
        role.role_code = role_code

    if "role_name" in payload:
        role_name = str(payload.get("role_name", "")).strip()
        if not role_name:
            raise InvalidUsageError("role_name 不能为空")
        role.role_name = role_name

    if "description" in payload:
        role.description = payload.get("description")

    if "status" in payload:
        status = str(payload.get("status", "")).strip()
        if status not in ALLOWED_STATUS:
            raise InvalidUsageError("status 仅支持 active 或 disabled")
        role.status = status

    if "extra_data" in payload:
        role.extra_data = payload.get("extra_data")

    try:
        db.session.flush()
    except IntegrityError as exc:
        raise ApiException(message="角色编码已存在", status_code=409) from exc

    return role_to_dict(role)


@transactional(db_error_message="状态更新失败，发生未知错误。")
def toggle_role_status(role_id, status):
    role = _get_role_or_404(role_id)
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError("status 仅支持 active 或 disabled")

    role.status = status
    return role_to_dict(role)


@transactional(db_error_message="删除角色失败，发生未知错误。")
def delete_role(role_id):
    role = _get_role_or_404(role_id)

    related_user_count = (
        User.query.with_entities(User.id).filter(User.role_id == role_id).count()
    )
    if related_user_count > 0:
        raise InvalidUsageError("无法删除该角色，请先取消相关用户的角色关联")

    related_permission_count = (
        RoleMappingPermission.query.with_entities(RoleMappingPermission.id)
        .filter(RoleMappingPermission.role_id == role_id)
        .count()
    )
    if related_permission_count > 0:
        raise InvalidUsageError("该角色存在关联权限，禁止删除")

    db.session.delete(role)
    return {"deleted": True, "role_id": role_id}
