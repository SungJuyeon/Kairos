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
from video_processing import apply_grayscale, apply_edge_detection

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT 설정
MQTT_BROKER = "172.30.1.68"  # MQTT 브로커 주소
MQTT_PORT = 1883
MQTT_TOPIC_VIDEO = "robot/video"

client = MQTTClient(client_id="fastapi_client")

async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_VIDEO)
    logger.info("구독 완료")

async def on_message(client, topic, payload, qos, properties):
    await process_message(topic, payload)

async def process_message(topic, payload):
    if topic == MQTT_TOPIC_VIDEO:
        logger.info("Received video frame")
        # 여기서는 각 필터를 적용할 수 있는 엔드포인트로 나누지 않고, 프레임을 그대로 반환합니다.
        # 프레임을 반환하는 부분은 각 엔드포인트에서 처리됩니다.

async def stream_video_frame(frame):
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

async def video_frame_generator():
    while True:
        await asyncio.sleep(0.1)  # 대기 시간 조정

@app.get("/video_feed")
async def get_video_feed():
    try:
        return StreamingResponse(video_frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.error(f"Error in get_video_feed: {e}")
        return HTMLResponse(content="Error in video stream", status_code=500)

@app.post("/apply_filter/grayscale")
async def apply_grayscale_filter():
    # 필터 적용을 위한 MQTT 메시지 수신을 처리하는 로직
    # 예시로, 수신된 프레임을 그레이스케일 필터에 적용
    # 실제로는 프레임을 MQTT에서 수신해야 하므로, 이를 구현해야 합니다.
    logger.info("Applying grayscale filter")
    # MQTT로부터 프레임 수신
    # frame_data = await get_frame_from_mqtt()  # 이 함수는 실제로 구현해야 합니다.
    # processed_frame = apply_grayscale(frame_data)
    # return StreamingResponse(processed_frame)  # 처리된 프레임을 반환
    return {"message": "Grayscale filter applied"}

@app.post("/apply_filter/edge_detection")
async def apply_edge_detection_filter():
    logger.info("Applying edge detection filter")
    # frame_data = await get_frame_from_mqtt()  # 이 함수는 실제로 구현해야 합니다.
    # processed_frame = apply_edge_detection(frame_data)
    # return StreamingResponse(processed_frame)
    return {"message": "Edge detection filter applied"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    client.on_message = on_message
    await on_connect()
    yield
    logger.info("종료")
    await client.disconnect()

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_fastapi():
    config = uvicorn.Config(app, port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_fastapi())
