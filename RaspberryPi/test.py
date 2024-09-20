import asyncio
import cv2
import time
import logging
import json
import random
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 현재 모터 상태를 저장하는 변수
wheel_direction = None
actuator_direction = None
wheel_speed = 100

# 카메라 설정
cap = cv2.VideoCapture(0)

# 바퀴 설정 #######################################################################
async def wheel_control(direction, duration=None):
    global wheel_direction
    wheel_direction = direction
    logging.info(f"바퀴 제어: 방향 {direction}, 속도 {wheel_speed}")

    if duration:
        await asyncio.sleep(duration)
        stop_wheel()
    else:
        while wheel_direction == direction:
            await asyncio.sleep(0.05)
        stop_wheel()

async def set_speed(speed):
    global wheel_speed
    wheel_speed = max(0, min(speed, 100))  # 속도를 0~100 사이로 제한
    logging.info(f"바퀴 속도 설정: {wheel_speed}")

def stop_wheel():
    global wheel_direction
    wheel_direction = None
    logging.info("바퀴 정지")

# 액추에이터 설정 ###############################################################
async def actuator_control(direction):
    global actuator_direction
    actuator_direction = direction
    logging.info(f"액추에이터 제어: 방향 {direction}")

    while actuator_direction == direction:
        await asyncio.sleep(0.1)

    stop_actuator()

def stop_actuator():
    global actuator_direction
    actuator_direction = None
    logging.info("액추에이터 정지")

# 거리 전송 ###################################################################
async def send_distance(client):
    while True:
        try:
            distance = measure_distance()
            if distance is not None:
                distance_message = json.dumps({"distance": distance})
                client.publish(MQTT_TOPIC_DISTANCE, distance_message)
                logging.info(f"거리 발행: {distance}")
            await asyncio.sleep(0.1)  # 전송 주기
        except Exception as e:
            logging.error(f"거리 전송 오류: {e}")
            await asyncio.sleep(1)

def measure_distance():
    # 실제 측정 대신 랜덤 값 반환
    return random.randint(1, 100)

# 영상 전송 ####################################################################
async def generate_frames(client):
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                logging.warning("프레임 캡처 실패")
                await asyncio.sleep(1)
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            client.publish(MQTT_TOPIC_VIDEO, frame_data)
            logging.info("비디오 프레임 전송")
            await asyncio.sleep(0.1)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"프레임 생성 오류: {e}")
            await asyncio.sleep(1)

# MQTT 설정
# MQTT_BROKER = "3.27.221.93"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"

client = MQTTClient(client_id="robot_controller_test")

async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logging.info("MQTT 브로커에 연결됨")
    client.subscribe(MQTT_TOPIC_COMMAND)
    logging.info(f"{MQTT_TOPIC_COMMAND} 토픽 구독")

async def on_message(client, topic, payload, qos, properties):
    command = json.loads(payload.decode('utf-8'))
    logging.info(f"명령 수신: {command}")

    if command["command"] == "stop_wheel":
        stop_wheel()
    elif command["command"] == "stop_actuator":
        stop_actuator()
    elif command["command"] in ["forward", "back", "left", "right"]:
        await wheel_control(command["command"])
    elif command["command"] in ["up", "down"]:
        await actuator_control(command["command"])
    elif command["command"] == "set_speed":
        await set_speed(command["speed"])
    else:
        logging.warning(f"잘못된 명령: {command}")

@asynccontextmanager
async def lifespan():
    client.on_message = on_message
    await on_connect()

    # 비동기 작업 시작
    asyncio.create_task(send_distance(client))
    asyncio.create_task(generate_frames(client))

    yield

    logging.info("프로그램 종료")
    await client.disconnect()
    cap.release()  # 카메라 리소스 해제

async def main():
    async with lifespan():
        stop_event = asyncio.Event()
        try:
            await stop_event.wait()
        except asyncio.CancelledError:
            logging.info("메인 루프 취소됨")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("사용자에 의해 프로그램 중단됨")
    finally:
        cap.release()  # 프로그램 종료 시 카메라 리소스 해제