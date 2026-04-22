from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
redis_client = FlaskRedis(decode_responses=True)
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")


def init_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    redis_client.init_app(app)
    socketio.init_app(app)
