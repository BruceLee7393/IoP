import os
import eventlet

eventlet.monkey_patch()

from backend.app import create_app  # noqa: E402
from backend.extensions import socketio  # noqa: E402


app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes", "on"}
    socketio.run(app, host=host, port=port, debug=debug)
