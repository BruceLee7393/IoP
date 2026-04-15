from backend.extensions import db
from backend.role.model import Role
from backend.user.model import User


def get_user_with_role_by_account(account):
    return (
        db.session.query(User)
        .outerjoin(Role, User.role_id == Role.id)
        .filter(User.account == account)
        .first()
    )
