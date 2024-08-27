# app.py
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
from gmqtt import Client as MQTTClient
import numpy as np
from Backend_Logic.hand_gesture import HandGestureRecognizer

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

# 상태 변수
distance_data = None
video_frames_queue = asyncio.Queue()  # 비디오 프레임 큐
voice_data = None
hand_gesture = True

# MQTT 설정
MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소 입력
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

client = MQTTClient(client_id="fastapi_client")

# 손동작 인식기 인스턴스 생성
try:
    gesture_recognizer = HandGestureRecognizer(model_path='models/model.keras')  # 확장자 변경
except Exception as e:
    logger.error(f"모델 로드 중 오류 발생: {e}")


async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    logger.info("구독 완료")


async def on_message(client, topic, payload, qos, properties):
    # logger.info(f"Message received on topic {topic}: {len(payload)} bytes")
    await process_message(topic, payload)


async def process_message(topic, payload):
    global voice_data, distance_data

    # 비디오 데이터 처리
    if topic == MQTT_TOPIC_VIDEO:
        # 현재 큐의 크기를 확인
        if video_frames_queue.qsize() >= 5:
            logger.warning("Video frame queue is full, dropping the oldest frame")
            await video_frames_queue.get()  # 오래된 프레임 삭제

        await video_frames_queue.put(payload)  # 비디오 프레임 큐에 추가
        logger.info(f"Video frames count: {video_frames_queue.qsize()}")
        return

    # 다른 데이터 유형 처리
    try:
        message = json.loads(payload.decode('utf-8'))  # JSON 디코딩
        # logger.info(f"Decoded message: {message}")

        if topic == MQTT_TOPIC_DISTANCE:
            distance_data = message["distance"]
            #logger.info(f"Received distance data: {distance_data}")

        elif topic == MQTT_TOPIC_COMMAND:
            voice_data = message["audio"]
            logger.info("Received audio data")

    except json.JSONDecodeError:
        logger.error(f"Received non-JSON message on topic {topic}")
    except UnicodeDecodeError:
        logger.error(f"Received non-UTF-8 message on topic {topic}, payload length: {len(payload)}")
    except Exception as e:
        logger.error(f"Error processing message on topic {topic}: {e}")


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


async def video_frame_generator():
    while True:
        try:
            frame = await video_frames_queue.get()  # 큐에서 프레임 가져오기
            img = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
            _, jpeg = cv2.imencode('.jpg', img)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            video_frames_queue.task_done()  # 작업 완료 표시
        except Exception as e:
            logger.error(f"Error while sending video frame: {e}")
            await asyncio.sleep(0.1)


@app.get("/video_feed")
async def get_video_frame():
    try:
        return StreamingResponse(video_frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.error(f"Error in get_video_frame: {e}")
        return HTMLResponse(content="Error in video stream", status_code=500)


@app.post("/set_hand_gesture/{state}")
async def set_hand_gesture(state: str):
    global hand_gesture
    if state.lower() == "on":
        hand_gesture = True
        return {"message": "Hand gesture mode enabled"}
    elif state.lower() == "off":
        hand_gesture = False
        return {"message": "Hand gesture mode disabled"}
    else:
        return {"error": "Invalid state"}, 400


async def voice_data_generator():
    while True:
        if voice_data:
            yield voice_data.encode('utf-8')
        await asyncio.sleep(0.1)


@app.get("/get_voice_data")
async def get_voice_data():
    return StreamingResponse(voice_data_generator(), media_type="application/octet-stream")


async def run_fastapi():
    config = uvicorn.Config(app, port=8000, workers=4)  # 워커 수를 조정
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_fastapi())
