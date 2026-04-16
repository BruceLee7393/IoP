from datetime import datetime, timezone

from flask_jwt_extended import create_access_token, decode_token

from backend.common.exceptions import AuthenticationError
from backend.extensions import redis_client
from backend.IoP_user.dao import get_user_with_role_by_account


class AuthService:
    def login(self, account, password):
        user = get_user_with_role_by_account(account)

        if not user:
            raise AuthenticationError('用户账号不存在。')

        if not user.verify_password(password):
            raise AuthenticationError('用户密码错误。')

        if user.status != 'active':
            raise AuthenticationError('该用户账号已被禁用，无法登录。')

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role_id},
        )

        decoded = decode_token(access_token)
        exp_ts = int(decoded['exp'])
        jti = decoded['jti']
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl_seconds = max(exp_ts - now_ts, 1)

        redis_client.setex(f'login_token:{jti}', ttl_seconds, access_token)
        redis_client.setex(f'user_login_state:{user.id}', ttl_seconds, 'online')

        user_info = {
            'id': user.id,
            'account': user.account,
            'full_name': user.full_name,
            'role': user.role_id,
            'role_name': user.role.role_name if user.role else None,
            'status': user.status,
        }

        return access_token, user_info

    def logout(self, user_id, jti, exp_ts, access_token):
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl_seconds = max(int(exp_ts or 0) - now_ts, 1)

        redis_client.delete(f'login_token:{jti}')
        if user_id:
            redis_client.delete(f'user_login_state:{user_id}')

        # Keep revoked token marker until token natural expiration.
        redis_client.setex(f'blacklisted_token:{jti}', ttl_seconds, access_token or 'revoked')


auth_service = AuthService()
