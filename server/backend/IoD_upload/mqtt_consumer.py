import json
import os

from paho.mqtt import client as mqtt_client

from backend.IoD_upload.dao import insert_upload_record
from backend.extensions import socketio


def init_upload_mqtt_listener(app):
    if app.extensions.get("iod_upload_mqtt_listener_ready"):
        return

    host = app.config.get("MQTT_HOST", "127.0.0.1")
    port = int(app.config.get("MQTT_PORT", 1883))
    topic = app.config.get("MQTT_UPLOAD_TOPIC", "iod/device/upload")
    client_id = app.config.get(
        "MQTT_CLIENT_ID", f"iop-iod-upload-consumer-{os.getpid()}"
    )

    callback_api_version = getattr(mqtt_client, "CallbackAPIVersion", None)
    if callback_api_version and hasattr(callback_api_version, "VERSION1"):
        client = mqtt_client.Client(
            client_id=client_id,
            callback_api_version=callback_api_version.VERSION1,
        )
    else:
        client = mqtt_client.Client(client_id=client_id)
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    def on_connect(_client, _userdata, _flags, rc):
        if rc == 0:
            app.logger.info("MQTT connected: %s:%s", host, port)
            _client.subscribe(topic)
            app.logger.info("MQTT subscribed topic: %s", topic)
        else:
            app.logger.error("MQTT connect failed, rc=%s", rc)

    def on_message(_client, _userdata, msg):
        with app.app_context():
            try:
                payload_text = msg.payload.decode("utf-8")
                payload = json.loads(payload_text)
            except Exception as exc:
                app.logger.exception("MQTT payload parse failed: %s", exc)
                return

            try:
                saved = insert_upload_record(payload)
            except Exception as exc:
                app.logger.exception("Upload record persist failed: %s", exc)
                return

            socketio.emit("new_upload_record", saved)

    def on_disconnect(_client, _userdata, rc):
        app.logger.warning("MQTT disconnected, rc=%s", rc)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(host, port, keepalive=60)
        client.loop_start()
        app.extensions["iod_upload_mqtt_listener_ready"] = True
        app.extensions["iod_upload_mqtt_client"] = client
    except Exception as exc:
        app.logger.exception("MQTT startup failed: %s", exc)
