import os

import click
import pymysql
from flask.cli import with_appcontext

from backend.extensions import db
from backend.IoP_mapping.model import Permission
from backend.IoP_role.model import Role
from backend.IoP_user.model import User


def _rebuild_database(target_db_name, db_host, db_port, db_user, db_password):
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        charset='utf8mb4',
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{target_db_name}`;")
            cursor.execute(
                f"CREATE DATABASE `{target_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
    finally:
        conn.close()


def _seed_in_fresh_app(target_db_name, db_host, db_port, db_user, db_password):
    from backend.app import create_app

    os.environ['DB_HOST'] = str(db_host)
    os.environ['DB_PORT'] = str(db_port)
    os.environ['DB_USER'] = str(db_user)
    os.environ['DB_PASSWORD'] = str(db_password or '')
    os.environ['DB_NAME'] = str(target_db_name)
    os.environ['AUTO_DB_BOOTSTRAP'] = '0'

    fresh_app = create_app(os.getenv('FLASK_CONFIG', 'dev'))

    with fresh_app.app_context():
        db.create_all()

        admin_role = Role(
            role_code='admin',
            role_name='管理员',
            description='系统管理员角色',
            status='active',
        )
        user_role = Role(
            role_code='user',
            role_name='普通用户',
            description='默认普通用户角色',
            status='active',
        )

        admin_user = User(
            account='admin',
            full_name='系统管理员',
            status='active',
            role=admin_role,
        )
        admin_user.set_password('123456')

        superadmin_user = User(
            account='superadmin',
            full_name='超级管理员',
            status='active',
            role=admin_role,
        )
        superadmin_user.set_password('123456')

        test_users = []
        for account in ['user01', 'user02', 'user03']:
            user = User(
                account=account,
                full_name=account,
                status='active',
                role=user_role,
            )
            user.set_password('123456')
            test_users.append(user)

        base_permissions = [
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
        permission_models = [
            Permission(permission_code=code, permission_name=name, description=description)
            for code, name, description in base_permissions
        ]

        try:
            db.session.add(admin_role)
            db.session.add(user_role)
            db.session.add(admin_user)
            db.session.add(superadmin_user)
            db.session.add_all(test_users)
            db.session.add_all(permission_models)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


@click.command('init-db')
@click.option('--target-db', 'target_db_name', envvar='INIT_DB_NAME', default='IoP', show_default=True)
@click.option('--db-host', envvar='DB_HOST', default='127.0.0.1', show_default=True)
@click.option('--db-port', envvar='DB_PORT', default=3306, type=int, show_default=True)
@click.option('--db-user', envvar='DB_USER', default='root', show_default=True)
@click.option('--db-password', envvar='DB_PASSWORD', default='', hide_input=True)
@with_appcontext
def init_db_command(target_db_name, db_host, db_port, db_user, db_password):
    """Rebuild MySQL IoP database, create tables, and seed base users."""
    try:
        _rebuild_database(target_db_name, db_host, db_port, db_user, db_password)
    except pymysql.MySQLError as exc:
        raise click.ClickException(
            f"MySQL连接或建库失败: {exc}. 请检查 --db-host/--db-port/--db-user/--db-password。"
        ) from exc

    _seed_in_fresh_app(target_db_name, db_host, db_port, db_user, db_password)

    click.echo('================ 初始化完成 ================')
    click.echo(f'数据库: {target_db_name}')
    click.echo('管理员账号:')
    click.echo('  - account=admin, password=123456')
    click.echo('  - account=superadmin, password=123456')
    click.echo('测试账号:')
    click.echo('  - account=user01, password=123456')
    click.echo('  - account=user02, password=123456')
    click.echo('  - account=user03, password=123456')
    click.echo('==========================================')


def register_commands(app):
    app.cli.add_command(init_db_command)
