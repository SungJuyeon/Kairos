import asyncio
import logging
import RPi.GPIO as GPIO

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

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 핀 설정
for pin in WHEEL_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
for pin in ACTUATOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    
# PWM 객체 생성 후 시작 (속도조절)

pwm_A = GPIO.PWM(WHEEL_PINS['ENA'], 100)  # 50Hz
pwm_B = GPIO.PWM(WHEEL_PINS['ENB'], 100)  # 50Hz
pwm_A.start(0)
pwm_B.start(0)
GPIO.output(WHEEL_PINS['IN1'], GPIO.LOW)
GPIO.output(WHEEL_PINS['IN2'], GPIO.LOW)
GPIO.output(WHEEL_PINS['IN3'], GPIO.LOW)
GPIO.output(WHEEL_PINS['IN4'], GPIO.LOW)


def wheel_control(direction):
    # 모터 방향 설정
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
    elif direction == "stop_wheel":
        GPIO.output(WHEEL_PINS['IN1'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN2'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN3'], GPIO.LOW)
        GPIO.output(WHEEL_PINS['IN4'], GPIO.LOW)
        set_speed(0)
    #logging.info(f"Setting wheel state to {direction}")


def set_speed(speed=50):
    pwm_A.ChangeDutyCycle(speed)  # ENA 핀에 속도 적용
    pwm_B.ChangeDutyCycle(speed)  # ENB 핀에 속도 적용
    #logging.info(f"Setting wheel speed to {speed}")



#############################################################################


# 액추에이터 설정 ###############################################################


def actuator_control(direction):
    logging.info(f"Setting actuator state to {direction}")
    if direction == "up":
        GPIO.output(ACTUATOR_PINS['IN4'], GPIO.HIGH)
        GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)
    elif direction == "down":
        GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)
        GPIO.output(ACTUATOR_PINS['IN3'], GPIO.HIGH)
    elif direction == "stop_actuator":
        GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)
        GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)
    #logging.info(f"Setting actuator state to {direction}")


#############################################################################