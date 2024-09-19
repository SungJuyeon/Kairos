import asyncio
import logging
import os
from typing import List
import json

import cv2
import httpx
import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse
from face_image_db import fetch_family_photos, current_userId
from face_recognition import recognize_periodically
from video_processing import generate_frames, video_frame_generator
#from models import Base, Message
from mqtt_client import setup_mqtt, distance_data, move, speed, video_frames

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")
user_photo_for_comparison = None
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#SPRING_BOOT_URL = "http://localhost:8080/user/id"
user_token = None  # 전역 변수로 토큰을 저장

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
    return {"distance": distance_data}

# async def fetch_user_id(token: str):
#     headers = {"Authorization": f"Bearer {token}"}
#     async with httpx.AsyncClient() as client:
#         response = await client.get(SPRING_BOOT_URL, headers=headers)
#         response.raise_for_status()
#         return response.json()
#
# async def current_userId(token: str):
#     user_id = await fetch_user_id(token)
#     return user_id

class TokenRequest(BaseModel):
    token: str

# 프론트엔드에서 JWT 토큰을 받는 엔드포인트
@app.post("/token")
async def set_token(token_request: TokenRequest):
    global user_token
    user_token = token_request.token
    await initialize_recognition()  # 토큰 설정 후 인식 초기화 작업 실행
    return {"message": "Token received"}

async def initialize_recognition():
    if not user_token:
        print("No token provided")
        return

    await setup_mqtt()

    user_id = await current_userId(user_token)
    fetch_family_photos(user_id)

    asyncio.create_task(recognize_periodically(video_frames, user_id))


@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/video_feed/{face}")
async def get_video_feed(face: bool):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
