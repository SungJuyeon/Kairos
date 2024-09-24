import queue
import cv2
import asyncio
import logging
import json
import random
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
import sounddevice as sd
import numpy as np

# 카메라 설정
cap = cv2.VideoCapture(0)
# 음성 캡처 큐
audio_queue = queue.Queue()

# 현재 모터 상태를 저장하는 변수
wheel_direction = None
actuator_direction = None
wheel_speed = 100

# 로깅 설정
logging.basicConfig(level=logging.INFO)


# 바퀴 설정 #######################################################################
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


async def set_speed(speed):
    global wheel_speed
    wheel_speed = max(0, min(speed, 100))  # 속도를 0~100 사이로 제한
    logging.info(f"wheel speed {wheel_speed}")
    if wheel_direction is not None:
        logging.info(f"Current direction: {wheel_direction}, speed applied: {wheel_speed}")


#############################################################################


# 액추에이터 설정 ###############################################################
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
#############################################################################


# 거리 전송 ###################################################################
async def send_distance(client):
    while True:
        try:
            distance = measure_distance()
            if distance is not None:
                distance_message = json.dumps({"distance": distance})  # JSON 형식으로 전송
                client.publish(MQTT_TOPIC_DISTANCE, distance_message)
                # logging.info(f"거리 발행: {distance}")
            await asyncio.sleep(0.1)  # 전송 주기
        except Exception as e:
            logging.error(f"Error in send_distance: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기


def measure_distance():
    # 1~100 랜덤 거리 반환
    distance = random.randint(20, 100)
    # logging.info(f"Measured distance: {distance}")
    return distance
#############################################################################


# 영상, 음성 전송 ####################################################################
async def generate_frames(client):
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to capture frame")
                await asyncio.sleep(1)  # 프레임 캡처 실패 시 대기
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            client.publish(MQTT_TOPIC_VIDEO, buffer.tobytes())  # 바이너리 형식 전송
            # logging.info("Sent a video frame")

            await asyncio.sleep(1 / 30)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"Error in generate_frames: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기


# 음성 캡처 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        logging.error(status)  # 오류 로그 남기기
    try:
        audio_queue.put(indata.copy())
        # logging.info(f"Audio data added to queue, frames: {frames}")  # 큐에 추가된 오디오 데이터 프레임 수 로깅
    except Exception as e:
        logging.error(f"Error in audio callback: {e}")
#############################################################################


# 오디오 설정################################################################
RATE = 44100
CHANNELS = 1
CHUNK = 1024

async def send_audio(client):
    def audio_callback(indata, frames, time, status):
        if status:
            logging.error(f"오디오 콜백 오류: {status}")
        audio_data = indata.tobytes()
        client.publish(MQTT_TOPIC_AUDIO, audio_data)

    with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=RATE, blocksize=CHUNK):
        while True:
            await asyncio.sleep(0.1)

##############################################################################
# MQTT 설정
#MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소 입력
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

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
        await set_speed(command["speed"])  # 속도 조절 명령 처리
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
    asyncio.create_task(send_audio(client))####################################################

    yield

    logging.info("종료")
    await client.disconnect()


async def main():
    async with lifespan():
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Interrupted by user, cleaning up...")
    finally:
        # 종료 처리
        cap.release()
        logging.info("Cleanup completed")