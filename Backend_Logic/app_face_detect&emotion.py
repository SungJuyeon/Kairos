import asyncio
import json
import logging
import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from gmqtt import Client as MQTTClient
from Backend_Logic.who_emotion_class import FaceRecognition

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

# State variables
distance_data = None
video_frames_queue = asyncio.Queue()
voice_data = None

# MQTT settings
MQTT_BROKER = "3.27.221.93"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"

client = MQTTClient(client_id="fastapi_client")

# Face recognition instance
face_recognition = FaceRecognition(
    registered_faces_folder='faces',
    model_prototxt='models/deploy.prototxt',
    model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
)

# MQTT connection and message processing
async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    logger.info("Subscribed to topics")

async def on_message(client, topic, payload, qos, properties):
    await process_message(topic, payload)

async def process_message(topic, payload):
    global distance_data, video_frames_queue

    if topic == MQTT_TOPIC_VIDEO:
        try:
            img_encode = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
            if img_encode is not None:
                if video_frames_queue.qsize() >= 5:
                    logger.warning("Video frame queue is full, dropping the oldest frame")
                    await video_frames_queue.get()
                await video_frames_queue.put(img_encode)
            else:
                logger.error("Failed to decode video frame")
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")

    elif topic == MQTT_TOPIC_DISTANCE:
        try:
            message = json.loads(payload.decode('utf-8'))
            distance_data = message.get("distance")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON message on topic {topic}")

# FastAPI app setup
app = FastAPI()

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

@app.get("/video_feed")
async def video_feed():
    async def video_frame_generator():
        while True:
            try:
                frame = await video_frames_queue.get()
                faces = face_recognition.detect_faces(frame)
                face_recognition.recognize_faces(frame, faces)
                face_recognition.draw_faces(frame, faces)

                _, jpeg = cv2.imencode('.jpg', frame)
                if jpeg is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
                else:
                    logger.error("Failed to encode frame as JPEG")
            except Exception as e:
                logger.error(f"Error generating video frame: {e}")
                await asyncio.sleep(0.1)

    return StreamingResponse(video_frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

async def lifespan(app: FastAPI):
    client.on_message = on_message
    await on_connect()
    yield
    await client.disconnect()

app.lifespan = lifespan

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
