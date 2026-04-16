import os

import pymysql
from pymysql import MySQLError
from sqlalchemy import inspect
from sqlalchemy.engine.url import make_url

from backend.extensions import db
from backend.IoP_role.model import Role


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
            inspector = inspect(db.engine)
            has_any_table = bool(inspector.get_table_names())
            if not has_any_table:
                db.create_all()
            _seed_base_roles_if_needed()
    except MySQLError as exc:
        raise RuntimeError(f'数据库自动初始化失败: {exc}') from exc
