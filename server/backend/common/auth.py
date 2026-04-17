from datetime import timedelta
from functools import wraps

from flask_jwt_extended import (
    create_access_token as flask_create_access_token,
    create_refresh_token as flask_create_refresh_token,
    get_jwt,
    verify_jwt_in_request,
)

from backend.common.exceptions import AuthenticationError


def create_access_token(user_id):
    return flask_create_access_token(
        identity=user_id,
        expires_delta=timedelta(minutes=30),
        additional_claims={
            'user_id': user_id,
            'type': 'access',
            'token_type': 'access',
        },
    )


def create_refresh_token(user_id):
    return flask_create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=7),
        additional_claims={
            'user_id': user_id,
            'type': 'refresh',
            'token_type': 'refresh',
        },
    )


def jwt_required(fn=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            token_type = claims.get('token_type') or claims.get('type')
            if token_type != 'access':
                raise AuthenticationError('无效的访问令牌类型')
            return func(*args, **kwargs)

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)


def jwt_required_refresh(fn=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            token_type = claims.get('token_type') or claims.get('type')
            if token_type != 'refresh':
                raise AuthenticationError('无效的刷新令牌类型')
            return func(*args, **kwargs)

        return wrapper

    if fn is None:
        return decorator
    return decorator(fn)
