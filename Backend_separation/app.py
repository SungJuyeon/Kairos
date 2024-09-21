import asyncio
import logging
import os
from typing import List
import json

import cv2
import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status, Header
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse, FileResponse

from calendar_app import get_all_schedules
from emotion_record import get_most_emotion_pic_path, get_most_frequent_emotion
from face_image_db import fetch_family_photos, current_userId
#validate_token
from face_recognition import recognize_periodically
from video_processing import generate_frames, video_frame_generator
from mqtt_client import setup_mqtt, distance_data, move, speed, video_frames

# 환경 변수에서 테스트 모드 설정 확인
TEST_MODE = True

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
user_photo_for_comparison = None
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await setup_mqtt()
    #asyncio.create_task(recognize_gesture_periodically(video_frames))
    asyncio.create_task(recognize_periodically(video_frames))

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/move/{direction}")
async def post_move(direction: str):
    await move(direction)

@app.post("/speed/{action}")
async def post_speed(action: str):
    await speed(action)

@app.get("/distance")
async def get_distance():
    logger.info(f"get_distance 엔드포인트 호출됨.")
    return {"distance": distance_data}

@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/video_feed/{face}")
async def get_video_feed(face: bool):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/calendar")
def calendar():
    schedules = get_all_schedules()
    return {"schedules": schedules}

# 프론트에서 Header에 " token: 사용자 토큰 " 전달해주기
@app.get("/most_emotion")
async def most_emotion(token: str = Header(...)):
    user_id = await current_userId(token)  # 비동기 함수 호출로 user_id 추출
    most_frequent_emotion = get_most_frequent_emotion(user_id)  # user_id로 감정 데이터 가져오기
    if most_frequent_emotion is None:
        raise HTTPException(status_code=404, detail="Emotion data not found.")
    return {"most_frequent_emotion": most_frequent_emotion}

# 프론트에서 Header에 " token: 사용자 토큰 " 전달해주기
@app.get("/most_emotion_pic")
async def most_emotion_pic(token: str = Header(...)):
    user_id = await current_userId(token)  # 비동기 함수 호출로 user_id 추출
    pic_path = get_most_emotion_pic_path(user_id)  # user_id로 사진 경로 가져오기
    if not os.path.exists(pic_path):
        raise HTTPException(status_code=404, detail="Emotion picture not found.")

    return FileResponse(pic_path, media_type="image/jpeg")

# @app.get("/gesture")
# async def get_gesture():
#     logger.info(f"get_gesture 엔드포인트 호출됨.")
#     from handgesture_recognition import this_action
#     return {"gesture": this_action}

if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())