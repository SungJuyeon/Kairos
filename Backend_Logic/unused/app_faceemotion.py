import asyncio
import json
import logging
from contextlib import asynccontextmanager
import cv2
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import numpy as np
from Backend_Logic.HandGestureRecognizer import HandGestureRecognizer
from Backend_Logic.unused.FaceRecognition import FaceRecognition
from gmqtt import Client as MQTTClient
import time

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

# 상태 변수
distance_data = None
video_frames_queue = asyncio.Queue()  # 비디오 프레임 큐
audio_data = None
hand_gesture = True



# MQTT 설정
MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

client = MQTTClient(client_id="fastapi_client")

# 얼굴 인식기 인스턴스 생성
face_recognition = FaceRecognition(
    registered_faces_folder='faces',
    model_prototxt='models/deploy.prototxt',
    model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
)

# 손동작 인식기 인스턴스 생성
try:
    gesture_recognizer = HandGestureRecognizer(model_path='../models/model.keras')
except Exception as e:
    logger.error(f"모델 로드 중 오류 발생: {e}")

# MQTT 연결 및 메시지 처리
async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    logger.info("구독 완료")


async def on_message(client, topic, payload, qos, properties):
    await process_message(topic, payload)


# 마지막 명령 발행 시간 초기화
last_command_time = 0
command_cooldown = 8  # 8초 쿨다운

async def gesture_action(action):
    global last_command_time  # 마지막 명령 발행 시간 사용

    current_time = time.time()  # 현재 시간 가져오기

    # 쿨다운 체크
    if current_time - last_command_time < command_cooldown:
        logger.info("Command is on cooldown. Ignoring action.")
        return  # cooldown 지나지 않았으면 명령 무시

    if action == 'come':
        command = json.dumps({"command": "forward"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: forward")
        last_command_time = current_time  # 명령 발행 시간 기록
        while True:
            if distance_data is not None and distance_data < 10:
                command = json.dumps({"command": "stop"})
                client.publish(MQTT_TOPIC_COMMAND, command)
                break
            await asyncio.sleep(0.1)  # 0.1초 대기하여 CPU 사용량을 줄임

    elif action == 'spin':
        command = json.dumps({"command": "right"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: right")
        last_command_time = current_time  # 명령 발행 시간 기록
        await asyncio.sleep(2)
        command = json.dumps({"command": "stop"})
        client.publish(MQTT_TOPIC_COMMAND, command)

    elif action == 'away':
        command = json.dumps({"command": "back"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: back")
        last_command_time = current_time  # 명령 발행 시간 기록
        await asyncio.sleep(2)
        command = json.dumps({"command": "stop"})
        client.publish(MQTT_TOPIC_COMMAND, command)


async def process_message(topic, payload):
    global video_frames_queue

    # 비디오 데이터 처리
    if topic == MQTT_TOPIC_VIDEO:
        if video_frames_queue.qsize() >= 5:
            logger.warning("Video frame queue is full, dropping the oldest frame")
            await video_frames_queue.get()  # 오래된 프레임 삭제

        img_encode = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
        await video_frames_queue.put(img_encode)  # 프레임을 큐에 추가

# 얼굴 인식 비디오 스트림 엔드포인트 추가
frame_interval = 7  # 5 프레임마다 처리
frame_counter = 0

async def face_video_frame_generator():
    global frame_counter
    while True:
        try:
            frame = await video_frames_queue.get()

            faces = face_recognition.detect_faces(frame)

            if frame_counter % frame_interval == 0:
                face_recognition.recognize_faces(frame, faces)

            face_recognition.draw_faces(frame, faces)
            frame_counter += 1

            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.1)


# 기존 API 엔드포인트들
@asynccontextmanager
async def lifespan(app: FastAPI):
    client.on_message = on_message
    await on_connect()
    yield
    logger.info("종료")
    await client.disconnect()

# FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/face_video_feed")
async def get_face_video_feed():
    return StreamingResponse(face_video_frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/move/{direction}")
async def move(direction: str):
    logger.info(f"Attempting to move {direction}")
    command = json.dumps({"command": direction})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logger.info(f"Command sent: {command}")

# 상태 변수 추가
current_speed = 100  # 현재 속도 초기화

@app.post("/speed/{action}")
async def speed(action: str):
    global current_speed
    logger.info(f"Attempting to set speed: {action}")

    if action == "up":
        current_speed = min(100, current_speed + 10)  # 속도를 10 증가, 최대 100으로 제한
    elif action == "down":
        current_speed = max(0, current_speed - 10)  # 속도를 10 감소, 최소 0으로 제한
    else:
        logger.warning(f"Invalid action for speed: {action}")
        return {"error": "Invalid action"}, 400

    command = json.dumps({"command": "set_speed", "speed": current_speed})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logger.info(f"Speed command sent: {command}")
    return {"message": "Speed command sent successfully", "current_speed": current_speed}

@app.get("/distance")
async def get_distance():
    return {"distance": distance_data}

async def run_fastapi():
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_fastapi())
