import cv2
import asyncio
import logging
import json
import random
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager

# 카메라 설정
cap = cv2.VideoCapture(0)

# 현재 모터 상태를 저장하는 변수
wheel_direction = None
actuator_direction = None
wheel_speed = 100

# 로깅 설정
logging.basicConfig(level=logging.INFO)

async def wheel_control(direction):
    global wheel_direction
    wheel_direction = direction
    logging.info(f"wheel {direction}, speed {wheel_speed}")

    while wheel_direction == direction:
        await asyncio.sleep(0.05)

    stop_wheel()

def stop_wheel():
    logging.info("Stopping motors")
    global wheel_direction
    wheel_direction = None

async def actuator_control(direction):
    global actuator_direction
    actuator_direction = direction
    logging.info(f"Setting actuator state to {direction}")

    while actuator_direction == direction:
        await asyncio.sleep(0.1)

    stop_actuator()

def stop_actuator():
    logging.info("Stopping actuator")
    global actuator_direction
    actuator_direction = None

async def send_distance(client):
    while True:
        try:
            # 랜덤 거리 생성 (10~100 사이)
            distance = random.randint(10, 100)
            distance_message = json.dumps({"distance": distance})  # JSON 형식으로 전송
            client.publish(MQTT_TOPIC_DISTANCE, distance_message)
            await asyncio.sleep(1)  # 전송 주기
        except Exception as e:
            logging.error(f"Error in send_distance: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기

async def generate_frames(client):
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to capture frame")
                await asyncio.sleep(1)  # 프레임 캡처 실패 시 대기
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            client.publish(MQTT_TOPIC_VIDEO, frame_data)
            await asyncio.sleep(1/30)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"Error in generate_frames: {e}")
            await asyncio.sleep(0.5)  # 오류 발생 시 대기

# MQTT 설정
MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소 입력
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"

client = MQTTClient(client_id="robot_controller")

async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logging.info("연결")
    client.subscribe(MQTT_TOPIC_COMMAND)
    logging.info("구독")

async def on_message(client, topic, payload, qos, properties):
    command = json.loads(payload.decode('utf-8'))
    logging.info(f"Received command: {command}")

    if command["command"] == "stop_wheel":
        stop_wheel()
    elif command["command"] == "stop_actuator":
        stop_actuator()
    elif command["command"] in ["forward", "back", "left", "right"]:
        await wheel_control(command["command"])
    elif command["command"] in ["up", "down"]:
        await actuator_control(command["command"])
    elif command["command"] == "set_speed":
        logging.info(f"Setting speed to {command['speed']}")
    else:
        logging.warning(f"Invalid command: {command}")

async def on_disconnect():
    logging.warning("Disconnected from MQTT broker, attempting to reconnect...")
    while True:
        try:
            await client.connect(MQTT_BROKER, MQTT_PORT)
            logging.info("Reconnected to MQTT broker")
            break
        except Exception as e:
            logging.error(f"Reconnect failed: {e}")
            await asyncio.sleep(5)  # 재시도 대기

@asynccontextmanager
async def lifespan():
    client.on_message = on_message
    await on_connect()

    # 비동기 작업 시작
    asyncio.create_task(send_distance(client))
    asyncio.create_task(generate_frames(client))

    yield

    logging.info("종료")
    await client.disconnect()

async def main():
    async with lifespan():
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        cap.release()
        logging.info("Cleanup completed")