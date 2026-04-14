# 导入 flask_jwt_extended 中的 create_access_token 函数
from flask_jwt_extended import create_access_token

# 导入用户 DAO 和密码加密工具
from backend.user import dao as user_dao
from backend.extensions import bcrypt, redis_client
# [新增] 导入我们自己的异常类
from backend.common.exceptions import AuthenticationError
from datetime import datetime, timezone, timedelta

class AuthService:
    """认证服务类，处理登录和JWT相关逻辑"""

    def login(self, account, password):
        """
        处理用户登录，验证成功则返回JWT。
        使用 Flask-JWT-Extended 来生成令牌。
        :param account: 用户账号
        :param password: 密码
        :return: access_token
        :raises AuthenticationError: 如果账号或密码错误、用户状态禁用
        """
        # 1. 根据用户名查找用户
        user = user_dao.get_user_by_account_login(account)

        # [修改]
        # 如果用户不存在，或者密码不匹配，都统一抛出认证失败异常
        if not user:
            raise AuthenticationError("用户账号不存在。")
        if not bcrypt.check_password_hash(user.password_hash, password):
            # [修改] 抛出明确的异常
            raise AuthenticationError("用户密码错误。")
        
        # [新增] 检查用户状态 - 只检查用户状态，不检查角色状态
        if user.status != 'active':
            raise AuthenticationError("该用户账号已被禁用，无法登录。")
            
        # 3. 定义附加到 JWT 中的自定义声明 (claims)
            # 我们可以把用户的角色等非敏感信息放在这里
        additional_claims = {"role": user.role_id}
        # 4. 创建 access token
        # a. 第一个参数 'identity' 是令牌的核心身份标识，我们用 user.id
        # b. additional_claims 会被合并到 JWT 的载荷中
        access_token = create_access_token(
            identity=user.id, 
            additional_claims=additional_claims
        )
        return access_token

    def logout(self, jwt_payload):
        """
        [新增] 处理用户登出逻辑的核心方法。
        它的主要工作是计算出令牌的剩余生命周期，然后将它的 jti 以相同的生命周期存入 Redis。
        """
        # 从令牌的载荷中获取 'jti'。'jti' 是每个 JWT 的唯一标识符。
        jti = jwt_payload['jti']

        # 从载荷中获取 'exp'，这是令牌的过期时间，它是一个 Unix 时间戳 (从1970年1月1日到现在的秒数)。
        expires_timestamp = jwt_payload['exp']

        # 获取当前的 UTC 时间。我们使用 UTC 时间是为了避免时区问题，这在服务器编程中是最佳实践。
        now_timestamp = datetime.now(timezone.utc)

        # 将令牌的过期时间戳 (一个数字) 转换为一个 datetime 对象，同样设置为 UTC 时区。
        expires_datetime = datetime.fromtimestamp(expires_timestamp, tz=timezone.utc)

        # 计算出从现在到令牌过期还剩下多少时间，结果是一个 timedelta 对象。
        time_left = expires_datetime - now_timestamp

        # 构造用于存储在 Redis 中的键名。
        redis_key = f"jwt_blacklist:{jti}"

        # [修复] 调用我们从 extensions.py 导入的 redis_client 实例，而不是 self.redis_client。
        # setex 是 "SET with EXpire" 的缩写，它原子性地完成两件事：
        # 1. SET redis_key "true" (将键的值设为 "true")
        # 2. EXPIRE redis_key time_left (将这个键的过期时间设置为 time_left)
        # 这样做可以确保 Redis 不会永久存储这些已登出的令牌，它们会自动被清理。
        redis_client.setex(redis_key, time_left, "true")

# 创建一个服务实例
auth_service = AuthService()
