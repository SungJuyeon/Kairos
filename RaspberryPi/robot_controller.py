import cv2
import asyncio
import RPi.GPIO as GPIO
import time
import logging
import json
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager

# 핀 번호 설정
MOTOR_PINS = {
    'ENA': 17,
    'IN1': 27,
    'IN2': 22,
    'IN3': 23,
    'IN4': 24,
    'ENB': 25
}

ULTRASONIC_PINS = {
    'TRIG': 20,
    'ECHO': 16
}

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 모터 핀 설정
for pin in MOTOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# 초음파 센서 핀 설정
GPIO.setup(ULTRASONIC_PINS['TRIG'], GPIO.OUT)
GPIO.setup(ULTRASONIC_PINS['ECHO'], GPIO.IN)

# 카메라 설정
cap = cv2.VideoCapture(0)

# 현재 모터 상태를 저장하는 변수
current_direction = None

# 로깅 설정
logging.basicConfig(level=logging.INFO)


async def motor_control(direction):
    global current_direction
    current_direction = direction
    logging.info(f"Setting motor state to {direction}")
    set_motor_state(direction)

    while current_direction == direction:
        await asyncio.sleep(0.1)

    stop()


def set_motor_state(direction):
    GPIO.output(MOTOR_PINS['ENA'], GPIO.HIGH)
    GPIO.output(MOTOR_PINS['ENB'], GPIO.HIGH)

    # 모터 방향 설정
    if direction == "forward":
        GPIO.output(MOTOR_PINS['IN1'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN2'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN3'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN4'], GPIO.LOW)
    elif direction == "back":
        GPIO.output(MOTOR_PINS['IN1'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN2'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN3'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN4'], GPIO.HIGH)
    elif direction == "left":
        GPIO.output(MOTOR_PINS['IN1'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN2'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN3'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN4'], GPIO.LOW)
    elif direction == "right":
        GPIO.output(MOTOR_PINS['IN1'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['IN2'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN3'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['IN4'], GPIO.HIGH)


def stop():
    logging.info("Stopping motors")
    global current_direction
    current_direction = None

    for pin in MOTOR_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    logging.info("Motors stopped")


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
    try:
        GPIO.output(ULTRASONIC_PINS['TRIG'], True)
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_PINS['TRIG'], False)

        pulse_start = time.time()
        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 0:
            pulse_start = time.time()

        pulse_end = time.time()
        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)
    except Exception as e:
        logging.error(f"Error measuring distance: {e}")
        return None


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
            # logging.info("Sent a video frame")
            await asyncio.sleep(0.1)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"Error in generate_frames: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기


# MQTT 설정
MQTT_BROKER = "172.30.1.68"  # MQTT 브로커 주소 입력
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

    if command["command"] == "stop":
        stop()
    elif command["command"] in ["forward", "back", "left", "right"]:
        await motor_control(command["command"])
    else:
        logging.warning(f"Invalid command: {command}")


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
        GPIO.cleanup()
        cap.release()
        logging.info("Cleanup completed")
