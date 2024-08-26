# relay_control.py
import RPi.GPIO as GPIO

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)

# 릴레이 핀 번호 설정
relay_pin = 17

# 릴레이 핀 출력으로 설정
GPIO.setup(relay_pin, GPIO.OUT)

def turn_on_relay():
    """릴레이를 켭니다."""
    GPIO.output(relay_pin, GPIO.HIGH)
    print("릴레이 ON")

def turn_off_relay():
    """릴레이를 끕니다."""
    GPIO.output(relay_pin, GPIO.LOW)
    print("릴레이 OFF")

def cleanup():
    """GPIO 설정을 정리합니다."""
    GPIO.cleanup()
