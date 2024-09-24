import asyncio
import json
import logging
import time
import RPi.GPIO as GPIO



ULTRASONIC_PINS = {
    'TRIG': 20,
    'ECHO': 16
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ULTRASONIC_PINS['TRIG'], GPIO.OUT)
GPIO.setup(ULTRASONIC_PINS['ECHO'], GPIO.IN)

send_distance_task = None
#send_distance 함수를 비동기작업 시작하는 함수
async def start_send_distance(client):
    global send_distance_task
    send_distance_task = asyncio.create_task(send_distance(client))
#비동기 작업중인 send_distance 함수를 종료하는 함수
async def stop_send_distance():
    global send_distance_task
    send_distance_task.cancel()
    send_distance_task = None


async def send_distance(client):
    while True:
        try:
            distance = measure_distance()
            if distance is not None:
                distance_message = json.dumps({"distance": distance})
                from robot_controller import MQTT_TOPIC_DISTANCE
                client.publish(MQTT_TOPIC_DISTANCE, distance_message)
                logging.info(f"거리 발행: {distance}")
            else:
                logging.warning("거리 측정 실패")
            await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"send_distance 오류: {e}")
            await asyncio.sleep(1)


def measure_distance():
    try:
        GPIO.output(ULTRASONIC_PINS['TRIG'], True)
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_PINS['TRIG'], False)

        pulse_start = time.time()
        pulse_end = pulse_start
        timeout = time.time() + 0.1

        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                raise Exception("Echo 시작 타임아웃")

        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                raise Exception("Echo 종료 타임아웃")

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)
    except Exception as e:
        logging.error(f"거리 측정 오류: {e}")
        return None
