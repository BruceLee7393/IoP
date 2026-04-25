import paho.mqtt.client as mqtt
import json
import time

# --- 核心配置 ---
# 实验室服务器公网 IP
MQTT_BROKER = "183.169.121.226"
MQTT_PORT = 1883  # 如果你服务器上 Mosquitto 改了端口，请同步修改

# 对应 C++ 代码中的 req_topic (上传主题)
SUB_TOPIC = "iod/device/upload"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{time.strftime('%H:%M:%S')}] 成功连接到实验室服务器")
        # 订阅设备上传的消息
        client.subscribe(SUB_TOPIC, qos=1)
        print(f"正在监听主题: {SUB_TOPIC}")
    else:
        print(f"连接失败，返回码: {rc}")


def on_message(client, userdata, msg):
    print("\n" + "=" * 50)
    print(f"收到设备数据 [Topic: {msg.topic}]")

    try:
        # 1. 解析 C++ 端发来的 Payload
        raw_data = msg.payload.decode()
        data = json.loads(raw_data)

        device_id = data.get("device_id", "unknown")
        msg_id = data.get("msg_id", "none")

        print(f"来自设备: {device_id}")
        print(f"消息内容: {data.get('event_record')}")

        # 2. 构造回复主题 (必须与 C++ 订阅的主题完全一致)
        # C++: "iod/device/down/device-local-001/ack"
        reply_topic = "iod/device/down/device-local-001/ack"

        # 3. 构造符合业务逻辑的 ACK 报文
        ack_payload = {
            "protocol": "IODS_DEVICE_EVENT_ACK",
            "msg_id": msg_id,
            "status": "success",
            "timestamp": int(time.time()),
            "message": "后端已同步收到并处理数据",
        }

        # 4. 发布 ACK (QoS 1 确保必达)
        client.publish(reply_topic, json.dumps(ack_payload), qos=1)
        print(f"已回复 ACK 至: {reply_topic}")
        print("=" * 50)

    except Exception as e:
        print(f"处理数据时出错: {e}")


# 启动 MQTT 客户端
client = mqtt.Client(client_id="iop_test_server")
client.on_connect = on_connect
client.on_message = on_message

print(f"正在启动后端模拟器，连接至 {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 进入无限循环监听模式
client.loop_forever()
