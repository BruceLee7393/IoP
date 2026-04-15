from flask import jsonify


def success_response(data):
    return jsonify({'code': 0, 'message': 'success', 'data': data}), 200
