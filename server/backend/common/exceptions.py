class ApiException(Exception):
    status_code = 500
    message = '服务器内部错误'

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        body = dict(self.payload or ())
        body.setdefault('code', self.status_code)
        body.setdefault('data', None)
        body['message'] = self.message
        return body


class InvalidUsageError(ApiException):
    status_code = 400
    message = '无效的请求'


class AuthenticationError(ApiException):
    status_code = 401
    message = '认证失败'
