from flask import jsonify


def _build_body(code, message, data):
    return {
        'code': code,
        'message': message,
        'data': data,
    }


def _response(data=None, message='操作成功', status=200, code=0):
    return jsonify(_build_body(code=code, message=message, data=data)), status


def ok(data=None, message='操作成功', status=200):
    return _response(data=data, message=message, status=status, code=0)
