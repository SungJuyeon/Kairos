# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

import asyncio
import logging
import os
from typing import List
import json

import cv2
import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi import Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse
import jwt  # PyJWT 라이브러리 필요
from jwt import PyJWKClient
from face_image_db import fetch_family_photos
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
    allow_origins=["*"],  # 필요에 따라 특정 도메인으로 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SPRING_BOOT_URL = "http://localhost:8080/user/id"

async def fetch_user_id():
    async with httpx.AsyncClient() as client:
        response = await client.get(SPRING_BOOT_URL)
        response.raise_for_status()
        return response.json()

async def current_userId():
    user_id = await fetch_user_id()
    return user_id

# async def current_userId():
#     return "3052"

@app.on_event("startup")
async def startup_event():
    global user_photo_for_comparison
    await setup_mqtt()
    user_id = await current_userId()
    fetch_family_photos(user_id)  # 가족 사진 저장
    print(f"Fetched User ID: {user_id}")
    asyncio.create_task(recognize_periodically(video_frames, user_id))



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


@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


# 현재 나의 감정(동영상) {face}에 ture 넣으면 됨
@app.get("/video_feed/{face}")
async def get_video_feed(face: bool):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')


# ##################################################################
# load_dotenv()
#
# DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
# DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
# DATABASE_SERVER = "whichx2.mysql.database.azure.com"
# DATABASE_NAME = "mypage"
#
# DATABASE_URL = (f"mssql+pyodbc://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}/{DATABASE_NAME}?driver=ODBC"
#                 f"+Driver+17+for+SQL+Server")
#
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base.metadata.reflect(bind=engine)  # 기존 테이블 반영
#
#
# class MessageCreate(BaseModel):
#     sender_id: int
#     receiver_id: int
#     content: str
#
#
# class MessageResponse(BaseModel):
#     id: int
#     sender_id: int
#     receiver_id: int
#     content: str
#
#
# @app.post("/messages/", response_model=MessageResponse)
# def create_message(message: MessageCreate):
#     db = SessionLocal()
#     msg = Message(sender_id=message.sender_id, receiver_id=message.receiver_id, content=message.content)
#     db.add(msg)
#     db.commit()
#     db.refresh(msg)
#     return msg
#
#
# @app.get("/messages/{user_id}", response_model=List[MessageResponse])
# def read_messages(user_id: int):
#     db = SessionLocal()
#     messages = db.query(Message).filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).all()
#     return messages
#
#
# # WebSocket 예시
# @app.websocket("/ws/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: int):
#     await websocket.accept()
#
#     # 메시지를 받는 동안 대기
#     while True:
#         data = await websocket.receive_text()
#         # 메시지 처리 로직
#         # 예를 들어, 메시지를 데이터베이스에 저장하고, 해당 사용자에게 전송
#
#         # 예: 메시지를 상대에게 전송
#         message_data = json.loads(data)
#         new_message = MessageCreate(sender_id=user_id, receiver_id=message_data['receiver_id'],
#                                     content=message_data['content'])
#         await create_message(new_message)  # 메시지를 저장하는 함수 호출
#
#         await websocket.send_text(f"Message sent to {message_data['receiver_id']}: {message_data['content']}")
#
#
# ###################################################################
if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())