import RPi.GPIO as GPIO
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from time import sleep

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
motor_thread = None  # 모터 동작 스레드 저장

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

    stop()  # 동작 종료 시 stop 함수 호출

def stop():
    print("Stopping motors")
    global current_direction
    with lock:
        current_direction = None

    for pin in PIN_CONFIG.values():
        GPIO.output(pin, GPIO.LOW)

    print("Motors stopped")

@app.post("/move/{direction}")
def move(direction: str):
    global motor_thread
    if motor_thread is not None and motor_thread.is_alive():
        stop()  # 현재 모터가 동작 중이면 정지

    motor_thread = threading.Thread(target=motor_control, args=(direction,))
    motor_thread.start()
    return {"message": f"Moving {direction}"}

@app.post("/stop")
def stop_motors():
    stop()
    return {"message": "Stopped"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
