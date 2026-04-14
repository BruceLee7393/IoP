from flask import Blueprint, request, jsonify, current_app
from backend.auth.service import auth_service
# [新增] 导入自定义异常
from backend.common.exceptions import AuthenticationError, InvalidUsageError
# [修改] 从 flask_jwt_extended 中额外导入 jwt_required 和 get_jwt
from flask_jwt_extended import jwt_required, get_jwt
# [新增] 从我们统一管理的 extensions.py 中导入 limiter 实例
from backend.extensions import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
# [新增] 为登录接口应用一个独立的、更严格的速率限制。
# 这个装饰器必须放在 @auth_bp.route 下面。
# "5 per minute" 定义了一个独立的规则：
# -> 对于这个特定的接口，同一个IP地址，每分钟最多只能尝试调用5次。
# 如果一个IP在1分钟内发起了第6次登录请求，它将会被自动拒绝，
# Flask会返回一个 HTTP 429 Too Many Requests 的错误响应，
# 从而有效地减缓暴力破解的速度。
@limiter.limit("5 per minute")
def login():
    """用户登录接口，成功返回 JWT access token"""
    data = request.get_json()
    if not data:
        raise InvalidUsageError("请求体不能为空")

    account = data.get('account')
    password = data.get('password')

    if not account or not password: 
        raise InvalidUsageError("用户账号和密码是必需的")

    # [修改] 使用 try...except 捕获业务异常
    try:
        access_token = auth_service.login(account, password)
        return jsonify({"access_token": access_token}), 200
    except AuthenticationError as e:
        # 捕获认证失败的异常，然后重新抛出
        # 它将被 app.py 中的全局异常处理器捕获并格式化成标准 JSON 响应
        raise e # 重新抛出，交给全局处理器处理
    except Exception:
        raise InvalidUsageError("登录失败，发生未知错误。")
    #如果 login 抛出了 AuthenticationError，我们就把它接住，然后重新抛出 (raise e)。你可能会觉得奇怪为什么要接住又马上扔出去
    #这是因为我们想让最终的异常能被 app.py 里的全局异常处理器统一处理，生成标准的 JSON 错误响应。


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    [新增] 用户登出接口。
    这个接口受 @jwt_required() 保护，所以必须在请求头中提供有效的 JWT 才能访问。
    """
    try:
        # 在受保护的端点中，调用 get_jwt() 可以获取到当前请求的令牌的载荷(payload)。
        # 这个载荷是一个字典，包含了 'jti', 'identity', 'exp' 等信息。
        jwt_payload = get_jwt()
        
        # 调用我们之前在 AuthService 中定义的 logout 方法，将载荷传递给它。
        auth_service.logout(jwt_payload)
        
        # 如果 service 层没有抛出异常，就说明登出成功。
        return jsonify({"message": "成功退出登录"}), 200
    except Exception as e:
        # 这里的异常可能是 Redis 连接失败等，我们暂时作为一个通用错误处理
        # 在真实的生产环境中，这里应该有更详细的日志记录。
        current_app.logger.error(f"退出登录时发生错误: {str(e)}")
        raise InvalidUsageError("退出登录失败，发生未知错误。")