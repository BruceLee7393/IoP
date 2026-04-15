from sqlalchemy.orm import joinedload

from backend.user.model import User


def get_user_with_role_by_account(account):
    return (
        User.query.options(joinedload(User.role))
        .filter(User.account == account)
        .first()
    )
