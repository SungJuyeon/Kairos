import RPi.GPIO as GPIO
import time

# GPIO 핀 설정
TRIG = 23  # 트리거 핀
ECHO = 24  # 에코 핀

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 센서 테스트 함수
def measure_distance():
    # 초음파 신호 송출
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10us 지속
    GPIO.output(TRIG, False)

    # 에코 신호 수신 대기
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # 거리 계산
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cm 단위
    distance = round(distance, 2)

    return distance

try:
    while True:
        distance = measure_distance()
        print(f"거리: {distance} cm")
        time.sleep(1)  # 1초 간격으로 측정

except KeyboardInterrupt:
    print("프로그램 종료")
    GPIO.cleanup()
