from backend.app import create_app
from backend.extensions import db
from backend.models import Role, User


def seed_test_user():
    app = create_app('dev')

    with app.app_context():
        db.create_all()

        role = Role.query.filter_by(role_code='admin').first()
        if not role:
            role = Role(role_code='admin', role_name='管理员', status='active')
            db.session.add(role)
            db.session.flush()

        user = User.query.filter_by(account='admin').first()
        if not user:
            user = User(
                account='admin',
                full_name='系统管理员',
                status='active',
                role_id=role.id,
            )
            user.set_password('123456')
            db.session.add(user)
        else:
            user.status = 'active'
            user.role_id = role.id
            user.set_password('123456')

        db.session.commit()
        print('seed ok -> account=admin password=123456')


if __name__ == '__main__':
    seed_test_user()
