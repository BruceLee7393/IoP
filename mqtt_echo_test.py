import paho.mqtt.client as mqtt

# --- 本地监听配置 ---
# 后端运行在本地，直接去本地 Mosquitto 拿数据
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
REQUEST_TOPIC = "iods/roles/sync/request"
CLIENT_ID = "iop-backend-test-02"


def on_connect(client, userdata, flags, rc):
    """连接成功后的回调函数"""
    if rc == 0:
        print(f"✅ 成功连接到本地 Mosquitto 代理: {MQTT_BROKER}")
        client.subscribe(REQUEST_TOPIC)
        print(f"🎧 正在监听主题: {REQUEST_TOPIC}")
        print("等待物理设备穿透公网发送数据...\n")
    else:
        print(f"❌ 连接失败，返回码: {rc}")


def on_message(client, userdata, msg):
    """收到消息后的回调函数"""
    # 提取并解码设备发来的原始报文
    try:
        payload_str = msg.payload.decode("utf-8")
    except UnicodeDecodeError:
        payload_str = str(msg.payload)

    print("\n" + "=" * 50)
    print("📥 叮！成功接收到公网隧道传来的数据：")
    print("-" * 50)
    # 原样打印所有内容
    print(payload_str)
    print("=" * 50 + "\n")


# --- 启动服务 ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

try:
    # 发起连接并保持永久运行
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 测试服务已手动停止")
except Exception as e:
    print(f"❌ 网络异常或配置错误: {e}")
