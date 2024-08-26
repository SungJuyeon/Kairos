# main.py
import time
from relay_control import turn_on_relay, turn_off_relay, cleanup

try:
    while True:
        turn_on_relay()
        time.sleep(2)  # 2초 대기
        turn_off_relay()
        time.sleep(2)  # 2초 대기

except KeyboardInterrupt:
    # 프로그램 종료 시 GPIO 정리
    cleanup()
