from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
redis_client = FlaskRedis(decode_responses=True)


def init_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    redis_client.init_app(app)
