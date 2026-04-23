from backend.common.datetime_utils import format_datetime_to_utc_z
from backend.common.exceptions import ApiException, InvalidUsageError
from backend.common.transaction import transactional
from backend.extensions import db
from backend.IoD_department.model import IodDepartment
from backend.IoD_mapping.model import IodUserDepartment


ALLOWED_STATUS = {0, 1}


def _format_datetime(value):
    return format_datetime_to_utc_z(value)


def _department_to_dict(dept):
    return {
        "id": dept.id,
        "dept_name": dept.dept_name,
        "status": int(dept.status),
        "created_at": _format_datetime(dept.created_at),
        "updated_at": _format_datetime(dept.updated_at),
    }


def _get_department_or_404(dept_id):
    dept = IodDepartment.query.filter(IodDepartment.id == dept_id).first()
    if not dept:
        raise ApiException(message="部门不存在", status_code=404)
    return dept


def list_departments(query_args):
    page = query_args.get("page", 1, type=int)
    per_page = query_args.get("per_page", 10, type=int)
    dept_name = query_args.get("dept_name", type=str)
    status = query_args.get("status", type=int)
    sort_by = str(query_args.get("sort_by", "created_at") or "created_at").strip()
    sort_order = str(query_args.get("sort_order", "desc") or "desc").strip()

    if page <= 0 or per_page <= 0:
        raise InvalidUsageError("page 和 per_page 必须大于 0")
    if status is not None and status not in ALLOWED_STATUS:
        raise InvalidUsageError("status 仅支持 0 或 1")

    query = IodDepartment.query
    if dept_name:
        query = query.filter(IodDepartment.dept_name.like(f"%{dept_name}%"))
    if status is not None:
        query = query.filter(IodDepartment.status == status)

    sort_map = {
        "dept_name": IodDepartment.dept_name,
        "status": IodDepartment.status,
        "created_at": IodDepartment.created_at,
        "updated_at": IodDepartment.updated_at,
    }
    sort_col = sort_map.get(sort_by, IodDepartment.created_at)
    query = query.order_by(sort_col.asc() if sort_order == "asc" else sort_col.desc())

    paged = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [_department_to_dict(item) for item in paged.items],
        "pagination": {
            "total": paged.total,
            "pages": paged.pages,
            "page": paged.page,
            "per_page": paged.per_page,
        },
    }


def get_department_detail(dept_id):
    dept = _get_department_or_404(dept_id)
    return _department_to_dict(dept)


@transactional(
    integrity_error_message="部门名称已存在",
    db_error_message="创建部门失败，数据库事务已回滚",
)
def create_department(payload):
    dept_name = str(payload.get("dept_name", "")).strip()
    status = payload.get("status", 1)

    if not dept_name:
        raise InvalidUsageError("dept_name 是必填项")
    if status not in ALLOWED_STATUS:
        raise InvalidUsageError("status 仅支持 0 或 1")

    existed = IodDepartment.query.filter(IodDepartment.dept_name == dept_name).first()
    if existed:
        raise ApiException(message="部门名称已存在", status_code=409)

    dept = IodDepartment(dept_name=dept_name, status=status)
    db.session.add(dept)
    db.session.flush()
    return _department_to_dict(dept)


@transactional(
    integrity_error_message="部门名称已存在",
    db_error_message="更新部门失败，数据库事务已回滚",
)
def update_department(dept_id, payload):
    dept = _get_department_or_404(dept_id)

    if "dept_name" in payload:
        dept_name = str(payload.get("dept_name", "")).strip()
        if not dept_name:
            raise InvalidUsageError("dept_name 不能为空")
        duplicated = (
            IodDepartment.query.filter(
                IodDepartment.dept_name == dept_name, IodDepartment.id != dept.id
            )
            .with_entities(IodDepartment.id)
            .first()
        )
        if duplicated:
            raise ApiException(message="部门名称已存在", status_code=409)
        dept.dept_name = dept_name

    if "status" in payload:
        status = payload.get("status")
        if status not in ALLOWED_STATUS:
            raise InvalidUsageError("status 仅支持 0 或 1")
        dept.status = status

    db.session.flush()
    return _department_to_dict(dept)


@transactional(db_error_message="删除部门失败，数据库事务已回滚")
def delete_department(dept_id):
    dept = _get_department_or_404(dept_id)

    related_user_count = (
        IodUserDepartment.query.with_entities(IodUserDepartment.user_id)
        .filter(IodUserDepartment.dept_id == dept_id)
        .count()
    )
    if related_user_count > 0:
        raise InvalidUsageError("该部门下仍有关联用户，无法删除")

    db.session.delete(dept)
    return {"deleted": True, "id": dept_id}
