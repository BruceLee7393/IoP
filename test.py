import paho.mqtt.client as mqtt
import json
import time

# --- 配置信息（必须指向你的实验室服务器） ---
MQTT_BROKER = "183.169.121.226"
MQTT_PORT = 1883
# 订阅 RK3568 发送请求的主题
SUB_TOPIC = "iod/device/upload"
# 这里的回复主题必须和你 C++ 代码里的 reply_topic 完全一致
PUB_TOPIC = "iod/device/down/device-rk3568-test/ack"


# 当连接成功时的回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"成功连接到服务器 {MQTT_BROKER}")
        # 开始订阅设备上传的消息
        client.subscribe(SUB_TOPIC)
        print(f"正在监听主题: {SUB_TOPIC}...")
    else:
        print(f"连接失败，返回码: {rc}")


# 当收到消息时的处理逻辑
def on_message(client, userdata, msg):
    print(f"\n[收到设备数据] 主题: {msg.topic}")
    try:
        # 解析收到 JSON 载荷
        data = json.loads(msg.payload.decode())
        print(f"设备ID: {data.get('device_id')}")
        print(f"事件内容: {data.get('event_record')}")

        # 构造给 C++ 端的回应（ACK）
        # 你的 C++ 代码正在等 response，我们发回一个简单的 JSON
        ack_payload = {
            "status": "success",
            "msg_id": data.get("msg_id"),
            "timestamp": int(time.time()),
            "detail": "Backend received your message!",
        }

        # 发布回复，让 C++ 端的 libhv_mqtt_sync_request 结束等待
        client.publish(PUB_TOPIC, json.dumps(ack_payload))
        print(f"已向 {PUB_TOPIC} 发送 ACK 回应")

    except Exception as e:
        print(f"数据解析失败: {e}")


# 启动客户端
client = mqtt.Client(client_id="iop-backend-tester")
client.on_connect = on_connect
client.on_message = on_message

print(f"正在尝试连接实验室服务器 {MQTT_BROKER}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 开启死循环监听
client.loop_forever()
