import RPi.GPIO as GPIO
from time import sleep
import threading

# 모터 제어 핀 설정
PIN_CONFIG = {
    'ENA': 17,
    'IN1': 27,
    'IN2': 22,
    'IN3': 23,
    'IN4': 24,
    'ENB': 25
}

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in PIN_CONFIG.values():
    GPIO.setup(pin, GPIO.OUT)

# 현재 모터 상태를 저장하는 변수
current_direction = None
lock = threading.Lock()

def set_motor_state(direction):
    GPIO.output(PIN_CONFIG['ENA'], GPIO.HIGH)
    GPIO.output(PIN_CONFIG['ENB'], GPIO.HIGH)

    if direction == "up":
        GPIO.output(PIN_CONFIG['IN1'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN2'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN3'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN4'], GPIO.LOW)
    elif direction == "down":
        GPIO.output(PIN_CONFIG['IN1'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN2'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN3'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN4'], GPIO.HIGH)
    elif direction == "left":
        GPIO.output(PIN_CONFIG['IN1'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN2'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN3'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN4'], GPIO.LOW)
    elif direction == "right":
        GPIO.output(PIN_CONFIG['IN1'], GPIO.HIGH)
        GPIO.output(PIN_CONFIG['IN2'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN3'], GPIO.LOW)
        GPIO.output(PIN_CONFIG['IN4'], GPIO.HIGH)

def motor_control(direction):
    global current_direction
    with lock:
        current_direction = direction

    set_motor_state(direction)

    while True:
        with lock:
            if current_direction != direction:
                break
        sleep(0.1)

    stop()

def stop():
    print("Stopping motors")
    global current_direction
    with lock:
        current_direction = None

    for pin in PIN_CONFIG.values():
        GPIO.output(pin, GPIO.LOW)

    print("Motors stopped")
