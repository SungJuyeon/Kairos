#app.py
import asyncio
import json
import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from gmqtt import Client as MQTTClient

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

# 상태 변수
distance_data = None
video_frames_queue = asyncio.Queue(maxsize=5)  # 비디오 프레임 큐
voice_data = None

# MQTT 설정
MQTT_BROKER = "172.30.1.68"  # MQTT 브로커 주소 입력
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

client = MQTTClient(client_id="fastapi_client")


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
        # logger.info("Received video frame")
        try:
            await video_frames_queue.put(payload)  # 비디오 프레임 큐에 추가
            logger.info(f"Video frames count: {video_frames_queue.qsize()}")
        except asyncio.QueueFull:
            logger.warning("Video frame queue is full, dropping the oldest frame")
            await video_frames_queue.get()  # 오래된 프레임 삭제
            await video_frames_queue.put(payload)  # 새 프레임 추가
            logger.info(f"Video frames count after dropping: {video_frames_queue.qsize()}")
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


@app.post("/move/{direction}")
async def move(direction: str):
    logger.info(f"Attempting to move {direction}")

    command = json.dumps({"command": direction})
    client.publish(MQTT_TOPIC_COMMAND, command)

    logger.info(f"Command sent: {command}")


@app.get("/distance")
async def get_distance():
    return {"distance": distance_data}


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def video_frame_generator():
    while True:
        try:
            frame = await video_frames_queue.get()  # 큐에서 프레임 가져오기
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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


async def voice_data_generator():
    while True:
        if voice_data:
            yield voice_data.encode('utf-8')
        await asyncio.sleep(0.1)


@app.get("/get_voice_data")
async def get_voice_data():
    return StreamingResponse(voice_data_generator(), media_type="application/octet-stream")


async def run_fastapi():
    config = uvicorn.Config(app, port=8000)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_fastapi())
