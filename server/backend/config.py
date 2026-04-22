import os
from datetime import timedelta
from urllib.parse import quote_plus


def _load_local_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def _build_database_uri():
    explicit_uri = (
        os.getenv("SQLALCHEMY_DATABASE_URI", "").strip()
        or os.getenv("DATABASE_URL", "").strip()
    )
    if explicit_uri:
        return explicit_uri

    db_user = os.getenv("DB_USER", "root")
    db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "IoP")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


_load_local_env_file()


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "iop-dev-secret-key-2026-very-long-secure-random-string-9f3d2a7c",
    )
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_DB_BOOTSTRAP = _as_bool(os.getenv("AUTO_DB_BOOTSTRAP", "1"), True)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "2")))

    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_UPLOAD_TOPIC = os.getenv("MQTT_UPLOAD_TOPIC", "iod/device/upload")
    MQTT_CLIENT_ID = os.getenv(
        "MQTT_CLIENT_ID", f"iop-iod-upload-consumer-{os.getpid()}"
    )


class DevelopmentConfig(Config):
    DEBUG = True


config_by_name = {
    "dev": DevelopmentConfig,
}
