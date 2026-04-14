from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from backend.common.exceptions import PermissionDeniedError
from backend.role.model import Permission
from backend.mapping.model import RolePermission
from backend.extensions import db
from backend.role.model import Role
import os
from dotenv import load_dotenv
def require_permissions(permission_codes, mode='any'):
    """权限检查装饰器。
    - permission_codes: str 或 List[str]
    - mode: 'any' 或 'all'，默认任一满足
    从 JWT 读取 role_id (claims['role'])，校验该角色是否拥有目标权限（未逻辑删除）。
    如果角色被禁用，视为拥有空权限列表，导致权限验证失败。
    """
    if isinstance(permission_codes, str):
        permission_codes = [permission_codes]

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            """先判断用户是不是管理员"""
            admin_id=get_jwt_identity()
            load_dotenv()
            super_admin_id=os.getenv('ADMIN')
            if super_admin_id and admin_id == super_admin_id:
                return fn(*args, **kwargs)
            
            
            """不是管理员再来判断权限"""
            claims = get_jwt()
            role_id = claims.get('role')
            if not role_id:
                raise PermissionDeniedError("未包含角色信息，拒绝访问")

            # 检查角色状态，如果角色被禁用或不存在，视为无任何权限

            role = db.session.query(Role).filter(
                Role.id == role_id
            ).first()
            
            if not role or role.status != 'active':
                # 角色不存在或被禁用时，视为没有任何权限，直接返回权限不足
                raise PermissionDeniedError("权限不足")

            # 通过 code -> id，再验证 role_permission
            perm_ids = [pid for (pid,) in db.session.query(Permission.id).filter(
                Permission.permission_code.in_(permission_codes)
            ).all()]

            if not perm_ids:
                raise PermissionDeniedError("权限校验失败：目标权限不存在或已删除")

            # 统计该 role 拥有的目标权限数量
            owned_count = db.session.query(RolePermission).\
                filter(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id.in_(perm_ids)
                ).count()

            if mode == 'all' and owned_count < len(perm_ids):
                raise PermissionDeniedError("权限不足")
            if mode == 'any' and owned_count == 0:
                raise PermissionDeniedError("权限不足")

            return fn(*args, **kwargs)
        return wrapper
    return decorator


