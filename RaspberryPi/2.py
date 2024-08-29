import cv2
import asyncio
import RPi.GPIO as GPIO
import time
import logging
import json
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager

# 핀 번호 설정
WHEEL_PINS = {
    'ENA': 17,
    'IN1': 27,
    'IN2': 22,
    'IN3': 23,
    'IN4': 24,
    'ENB': 25
}
ACTUATOR_PINS = {
    'IN3': 13,
    'IN4': 19
}
ULTRASONIC_PINS = {
    'TRIG': 20,
    'ECHO': 16
}

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 핀 설정
for pin in WHEEL_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
for pin in ACTUATOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
GPIO.setup(ULTRASONIC_PINS['TRIG'], GPIO.OUT)
GPIO.setup(ULTRASONIC_PINS['ECHO'], GPIO.IN)

# PWM 객체 생성 후 시작
pwm_A = GPIO.PWM(WHEEL_PINS['ENA'], 100)  # 100Hz
pwm_B = GPIO.PWM(WHEEL_PINS['ENB'], 100)  # 100Hz
pwm_A.start(0)
pwm_B.start(0)

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
    set_wheel_state(direction)

    while wheel_direction == direction:
        await asyncio.sleep(0.1)

    stop_wheel()

def set_wheel_state(direction):
    if direction == "forward":
        GPIO.output(WHEEL_PINS['IN1'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN2'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN3'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN4'], GPIO.LOW)
    elif direction == "back":
        GPIO.output(WHEEL_PINS['IN1'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN2'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN3'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN4'], GPIO.HIGH)
    elif direction == "left":
        GPIO.output(WHEEL_PINS['IN1'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN2'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN3'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN4'], GPIO.LOW)
    elif direction == "right":
        GPIO.output(WHEEL_PINS['IN1'], GPIO.HIGH)
        GPIO.output(WHEEL_PINS['IN2'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN3'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN4'], GPIO.HIGH)

    pwm_A.ChangeDutyCycle(wheel_speed)
    pwm_B.ChangeDutyCycle(wheel_speed)

async def set_speed(speed):
    global wheel_speed
    wheel_speed = max(0, min(speed, 100))  # 속도를 0~100 사이로 제한
    logging.info(f"wheel speed {wheel_speed}")
    if wheel_direction is not None:
        set_wheel_state(wheel_direction)  # 현재 방향에 속도 적용

def stop_wheel():
    logging.info("Stopping motors")
    global wheel_direction
    wheel_direction = None

    pwm_A.ChangeDutyCycle(0)
    pwm_B.ChangeDutyCycle(0)
    for pin in WHEEL_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    logging.info("Motors stopped")

async def actuator_control(direction):
    global actuator_direction
    actuator_direction = direction
    logging.info(f"Setting actuator state to {direction}")
    set_actuator_state(direction)

    while actuator_direction == direction:
        await asyncio.sleep(0.1)

    stop_actuator()

def set_actuator_state(direction):
    logging.info(f"Setting actuator state to {direction}")
    if direction == "up":
        GPIO.output(ACTUATOR_PINS['IN4'], GPIO.HIGH)
        GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)
    elif direction == "down":
        GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)
        GPIO.output(ACTUATOR_PINS['IN3'], GPIO.HIGH)

def stop_actuator():
    logging.info("Stopping actuator")
    global actuator_direction
    actuator_direction = None

    for pin in ACTUATOR_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    logging.info("Actuator stopped")

async def send_distance(client):
    while True:
        try:
            distance = await asyncio.to_thread(measure_distance)
            if distance is not None:
                distance_message = json.dumps({"distance": distance})  # JSON 형식으로 전송
                client.publish(MQTT_TOPIC_DISTANCE, distance_message)
                logging.info(f"거리 발행: {distance}")
            await asyncio.sleep(1)  # 전송 주기
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
        distance = pulse_duration * 17150  # 거리 계산 (cm)
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
            logging.info("Sent a video frame")
            await asyncio.sleep(1)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"Error in generate_frames: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기

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
    try:
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
    except Exception as e:
        logging.error(f"Error processing message: {e}")

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
        logging.info("Program interrupted. Cleaning up...")
    finally:
        GPIO.cleanup()
        cap.release()
        logging.info("Cleanup completed")
