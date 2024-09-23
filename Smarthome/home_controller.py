import asyncio
import json
import cv2
import RPi.GPIO as GPIO
from gmqtt import Client as MQTTClient

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED 핀 설정
LED_PIN = 20
GPIO.setup(LED_PIN, GPIO.OUT)

# 인덕션 핀 설정
INDUCTION_PIN = 21
GPIO.setup(INDUCTION_PIN, GPIO.OUT)

# 릴레이 핀 설정
RELAY_PIN = 13
GPIO.setup(RELAY_PIN, GPIO.OUT)

# 카메라 설정
cap = cv2.VideoCapture(0)

# MQTT 설정
MQTT_BROKER = "3.27.221.93"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "home/commands"
MQTT_TOPIC_VIDEO = "home/video"

client = MQTTClient("home_controller")

# light 제어 함수
def control_light(state):
    GPIO.output(LED_PIN, state)
    print(f"light {'ON' if state else 'OFF'}")
    
# induction 제어 함수
def control_induction(state):
    GPIO.output(LED_PIN, state)
    print(f"induction {'ON' if state else 'OFF'}")    

# 릴레이 제어 함수
def control_relay(state):
    GPIO.output(RELAY_PIN, state)
    print(f"Relay {'ON' if state else 'OFF'}")

# MQTT 메시지 처리
async def on_message(client, topic, payload, qos, properties):
    command = json.loads(payload.decode())
    if command["device"] == "led":
        control_light(command["state"])
    elif command["device"] == "induction":
        control_induction(command["state"])
    elif command["device"] == "relay":
        control_relay(command["state"])

# 카메라 프레임 전송
async def send_camera_frames():
    while True:
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            client.publish(MQTT_TOPIC_VIDEO, buffer.tobytes())
        await asyncio.sleep(0.05)

# MQTT 연결
async def connect_mqtt():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC_COMMAND)
    print("Connected to MQTT broker")

async def main():
    client.on_message = on_message
    await connect_mqtt()
    
    # 카메라 프레임 전송 태스크 시작
    asyncio.create_task(send_camera_frames())
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("프로그램 종료")
    finally:
        GPIO.cleanup()
        cap.release()