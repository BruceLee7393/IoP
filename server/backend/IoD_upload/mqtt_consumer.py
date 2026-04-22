import json
import os
import datetime
from json import JSONDecodeError

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
            raw_payload = msg.payload or b""
            payload_text = raw_payload.decode("utf-8", errors="replace").strip()

            if not payload_text:
                app.logger.warning(
                    "MQTT empty payload ignored, topic=%s",
                    msg.topic,
                )
                return

            try:
                payload = json.loads(payload_text)
            except JSONDecodeError as exc:
                preview = payload_text[:160]
                app.logger.warning(
                    "MQTT non-JSON payload ignored, topic=%s, reason=%s, preview=%s",
                    msg.topic,
                    exc,
                    preview,
                )
                return
            except Exception as exc:
                app.logger.warning(
                    "MQTT payload decode failed, topic=%s, reason=%s", msg.topic, exc
                )
                return

            if not isinstance(payload, dict):
                app.logger.warning(
                    "MQTT JSON payload is not object and ignored, topic=%s, type=%s",
                    msg.topic,
                    type(payload).__name__,
                )
                return

            # --- 核心字段提取与校验 ---
            msg_id = payload.get("msg_id")
            device_id = str(payload.get("device_id", "")).strip()

            if not msg_id or not device_id:
                app.logger.error(
                    "MQTT payload missing msg_id or device_id, ignored. topic=%s, preview=%s",
                    msg.topic,
                    payload_text[:160],
                )
                return

            saved = None
            ack_status = "OK"
            ack_code = 0
            ack_message = "db commit success"

            # --- 存库尝试与幂等拦截 ---
            try:
                # 即使触发了幂等拦截，这里也会正常返回原有的数据对象
                saved = insert_upload_record(payload)
            except Exception as exc:
                app.logger.exception("Upload record persist failed: %s", exc)
                ack_status = "FAIL"
                ack_code = 500
                ack_message = str(exc)[:200]

            # --- 构造并下发业务 ACK 回执 ---
            try:
                server_time = (
                    datetime.datetime.now(datetime.timezone.utc)
                    .astimezone()
                    .isoformat()
                )

                ack_payload = {
                    "msg_id": msg_id,
                    "status": ack_status,
                    "code": ack_code,
                    "message": ack_message,
                    "server_time": server_time,
                }

                ack_topic = f"iod/device/down/{device_id}/ack"
                _client.publish(ack_topic, json.dumps(ack_payload))
                app.logger.info(
                    "MQTT ACK published to topic: %s, msg_id: %s, status: %s",
                    ack_topic,
                    msg_id,
                    ack_status,
                )
            except Exception as exc:
                app.logger.exception("MQTT ACK publish failed: %s", exc)

            # --- 触发前端实时渲染 ---
            if saved:
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
