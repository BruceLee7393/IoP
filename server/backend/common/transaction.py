from functools import wraps

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.common.exceptions import ApiException, InvalidUsageError
from backend.extensions import db


def transactional(
    _func=None,
    *,
    commit=True,
    integrity_error_message='数据完整性约束冲突',
    db_error_message='数据库事务执行失败',
):
    """
    Decorator to provide consistent transaction handling.

    - On success: commits session when commit=True.
    - On IntegrityError: rollback + raise InvalidUsageError(400).
    - On SQLAlchemyError: rollback + raise ApiException(500).
    - On ApiException/other errors: rollback + re-raise.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if commit:
                    db.session.commit()
                return result
            except IntegrityError as exc:
                db.session.rollback()
                raise InvalidUsageError(integrity_error_message) from exc
            except SQLAlchemyError as exc:
                db.session.rollback()
                raise ApiException(db_error_message, status_code=500) from exc
            except ApiException:
                db.session.rollback()
                raise
            except Exception as exc:
                db.session.rollback()
                raise ApiException(db_error_message, status_code=500) from exc

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
