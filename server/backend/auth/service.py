from datetime import datetime, timezone

from flask_jwt_extended import decode_token

from backend.common.auth import create_access_token, create_refresh_token
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

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        access_exp_ts = int(access_decoded['exp'])
        refresh_exp_ts = int(refresh_decoded['exp'])
        access_jti = access_decoded['jti']
        refresh_jti = refresh_decoded['jti']
        access_ttl_seconds = max(access_exp_ts - now_ts, 1)
        refresh_ttl_seconds = max(refresh_exp_ts - now_ts, 1)

        redis_client.setex(f'login_token:{access_jti}', access_ttl_seconds, access_token)
        redis_client.setex(f'refresh_token:{refresh_jti}', refresh_ttl_seconds, refresh_token)
        redis_client.setex(f'user_login_state:{user.id}', access_ttl_seconds, 'online')
        redis_client.setex(f'user_refresh_state:{user.id}', refresh_ttl_seconds, refresh_jti)

        user_info = {
            'id': user.id,
            'account': user.account,
            'full_name': user.full_name,
            'role': user.role_id,
            'role_name': user.role.role_name if user.role else None,
            'status': user.status,
        }

        return access_token, refresh_token, user_info

    def refresh_access_token(self, user_id, refresh_jti):
        if not refresh_jti:
            raise AuthenticationError('无效的刷新令牌')

        refresh_token = redis_client.get(f'refresh_token:{refresh_jti}')
        if not refresh_token:
            raise AuthenticationError('刷新令牌已失效，请重新登录')

        access_token = create_access_token(user_id)
        decoded = decode_token(access_token)
        exp_ts = int(decoded['exp'])
        access_jti = decoded['jti']
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl_seconds = max(exp_ts - now_ts, 1)

        redis_client.setex(f'login_token:{access_jti}', ttl_seconds, access_token)
        redis_client.setex(f'user_login_state:{user_id}', ttl_seconds, 'online')

        return access_token

    def logout(self, user_id, jti, exp_ts, access_token, refresh_jti=None, refresh_exp_ts=None):
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl_seconds = max(int(exp_ts or 0) - now_ts, 1)

        redis_client.delete(f'login_token:{jti}')
        if refresh_jti:
            redis_client.delete(f'refresh_token:{refresh_jti}')
        if user_id:
            redis_client.delete(f'user_login_state:{user_id}')
            redis_client.delete(f'user_refresh_state:{user_id}')

        # Keep revoked token marker until token natural expiration.
        redis_client.setex(f'blacklisted_token:{jti}', ttl_seconds, access_token or 'revoked')
        if refresh_jti:
            refresh_ttl_seconds = max(int(refresh_exp_ts or 0) - now_ts, 1)
            redis_client.setex(f'blacklisted_token:{refresh_jti}', refresh_ttl_seconds, 'revoked')


auth_service = AuthService()
