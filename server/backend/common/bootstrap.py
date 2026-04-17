import os

import pymysql
from pymysql import MySQLError
from sqlalchemy.engine.url import make_url

from backend.extensions import db
from backend.IoP_mapping.model import Permission
from backend.IoP_role.model import Role
from backend.IoP_user.model import User


def _is_mysql_uri(db_uri):
    try:
        url = make_url(db_uri)
    except Exception:
        return False
    return (url.drivername or '').startswith('mysql')


def _ensure_database_exists(db_uri):
    url = make_url(db_uri)
    db_name = url.database
    if not db_name:
        raise RuntimeError('SQLALCHEMY_DATABASE_URI 缺少数据库名称。')

    conn = pymysql.connect(
        host=url.host or os.getenv('DB_HOST', '127.0.0.1'),
        port=int(url.port or os.getenv('DB_PORT', '3306')),
        user=url.username or os.getenv('DB_USER', 'root'),
        password=url.password or os.getenv('DB_PASSWORD', ''),
        charset='utf8mb4',
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
    finally:
        conn.close()


def _seed_base_roles_if_needed():
    wanted_roles = [
        {
            'role_code': 'admin',
            'role_name': '管理员',
            'description': '系统管理员角色',
            'status': 'active',
        },
        {
            'role_code': 'user',
            'role_name': '普通用户',
            'description': '默认普通用户角色',
            'status': 'active',
        },
    ]

    existing_codes = {item[0] for item in db.session.query(Role.role_code).all()}
    to_insert = [Role(**payload) for payload in wanted_roles if payload['role_code'] not in existing_codes]

    if not to_insert:
        return

    db.session.add_all(to_insert)
    db.session.commit()


def _seed_base_permissions_if_needed():
    # 采用 system:module:menu:action 命名规范，首页权限不落库。
    wanted_permissions = [
        ('iop:system:user:view', 'IoP-用户查看', '查看 IoP 用户列表'),
        ('iop:system:user:create', 'IoP-用户新增', '新增 IoP 用户'),
        ('iop:system:user:update', 'IoP-用户编辑', '编辑 IoP 用户'),
        ('iop:system:user:delete', 'IoP-用户删除', '删除 IoP 用户'),
        ('iop:system:role:view', 'IoP-角色查看', '查看 IoP 角色列表'),
        ('iop:system:role:create', 'IoP-角色新增', '新增 IoP 角色'),
        ('iop:system:role:update', 'IoP-角色编辑', '编辑 IoP 角色'),
        ('iop:system:role:delete', 'IoP-角色删除', '删除 IoP 角色'),
        ('iod:system:user:view', 'IoD-用户查看', '查看 IoD 用户列表'),
        ('iod:system:user:create', 'IoD-用户新增', '新增 IoD 用户'),
        ('iod:system:user:update', 'IoD-用户编辑', '编辑 IoD 用户'),
        ('iod:system:user:delete', 'IoD-用户删除', '删除 IoD 用户'),
        ('iod:system:role:view', 'IoD-角色查看', '查看 IoD 角色列表'),
        ('iod:system:role:create', 'IoD-角色新增', '新增 IoD 角色'),
        ('iod:system:role:update', 'IoD-角色编辑', '编辑 IoD 角色'),
        ('iod:system:role:delete', 'IoD-角色删除', '删除 IoD 角色'),
        ('iod:system:department:view', 'IoD-部门查看', '查看 IoD 部门列表'),
        ('iod:system:department:create', 'IoD-部门新增', '新增 IoD 部门'),
        ('iod:system:department:update', 'IoD-部门编辑', '编辑 IoD 部门'),
        ('iod:system:department:delete', 'IoD-部门删除', '删除 IoD 部门'),
    ]

    existing_codes = {
        item[0] for item in db.session.query(Permission.permission_code).all()
    }

    to_insert = [
        Permission(permission_code=code, permission_name=name, description=description)
        for code, name, description in wanted_permissions
        if code not in existing_codes
    ]

    if not to_insert:
        return

    db.session.add_all(to_insert)
    db.session.commit()


def _seed_superadmin_user_if_needed():
    admin_role = Role.query.filter(Role.role_code == 'admin').first()
    if not admin_role:
        return

    superadmin = User.query.filter(User.account == 'superadmin').first()
    if not superadmin:
        superadmin = User(
            account='superadmin',
            full_name='超级管理员',
            status='active',
            role_id=admin_role.id,
            gender='none',
        )
        superadmin.set_password('123456')
        db.session.add(superadmin)
        db.session.commit()
        return

    changed = False
    if superadmin.full_name != '超级管理员':
        superadmin.full_name = '超级管理员'
        changed = True
    if superadmin.status != 'active':
        superadmin.status = 'active'
        changed = True
    if superadmin.role_id != admin_role.id:
        superadmin.role_id = admin_role.id
        changed = True

    if changed:
        db.session.commit()


def ensure_database_ready(app):
    if not app.config.get('AUTO_DB_BOOTSTRAP', True):
        return

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri:
        raise RuntimeError('缺少 SQLALCHEMY_DATABASE_URI 配置。')

    try:
        if _is_mysql_uri(db_uri):
            _ensure_database_exists(db_uri)

        with app.app_context():
            # create_all is idempotent: it only creates tables that do not exist.
            db.create_all()
            _seed_base_roles_if_needed()
            _seed_base_permissions_if_needed()
            _seed_superadmin_user_if_needed()
    except MySQLError as exc:
        raise RuntimeError(f'数据库自动初始化失败: {exc}') from exc
