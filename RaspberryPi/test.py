import RPi.GPIO as GPIO
import time

# 액추에이터 핀 설정
ACTUATOR_PINS = {
    'IN3': 13,
    'IN4': 19
}

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)

# 핀 설정
GPIO.setup(ACTUATOR_PINS['IN3'], GPIO.OUT)
GPIO.setup(ACTUATOR_PINS['IN4'], GPIO.OUT)

try:
    # 액추에이터를 위로 이동
    print("Moving actuator up...")
    GPIO.output(ACTUATOR_PINS['IN3'], GPIO.HIGH)  # IN3에 HIGH 신호
    GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)   # IN4에 LOW 신호
    time.sleep(2)  # 2초 동안 작동

    # 액추에이터 정지
    GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)
    GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)
    time.sleep(1)  # 1초 대기

    # 액추에이터를 아래로 이동
    print("Moving actuator down...")
    GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)   # IN3에 LOW 신호
    GPIO.output(ACTUATOR_PINS['IN4'], GPIO.HIGH)  # IN4에 HIGH 신호
    time.sleep(2)  # 2초 동안 작동

    # 액추에이터 정지
    GPIO.output(ACTUATOR_PINS['IN3'], GPIO.LOW)
    GPIO.output(ACTUATOR_PINS['IN4'], GPIO.LOW)

finally:
    # GPIO 정리
    GPIO.cleanup()
    print("Cleanup completed")
