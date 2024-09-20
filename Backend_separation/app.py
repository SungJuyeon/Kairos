# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

# app.py
import asyncio
import logging
import os
from typing import List
import json

import cv2
import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse
import jwt
from face_image_db import fetch_family_photos, validate_token
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

SPRING_BOOT_URL = "http://localhost:8080/user/id"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.info(f"get_current_user 함수 호출됨. TEST_MODE: {TEST_MODE}")
    if TEST_MODE:
        logger.info("테스트 모드 활성화: 테스트 사용자 반환")
        return {"id": "test_user", "username": "tester"}
    
    try:
        user = await validate_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 정보",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"토큰 검증 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 처리 중 오류 발생",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.on_event("startup")
async def startup_event():
    logger.info(f"애플리케이션 시작. TEST_MODE: {TEST_MODE}")
    await setup_mqtt()

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/move/{direction}")
async def post_move(direction: str, current_user: dict = Depends(get_current_user)):
    await move(direction)

@app.post("/speed/{action}")
async def post_speed(action: str, current_user: dict = Depends(get_current_user)):
    await speed(action)

@app.get("/distance")
async def get_distance(current_user: dict = Depends(get_current_user)):
    logger.info(f"get_distance 엔드포인트 호출됨. 사용자: {current_user}")
    return {"distance": distance_data}

@app.get("/video")
async def video_stream(current_user: dict = Depends(get_current_user)):
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/video_feed/{face}")
async def get_video_feed(face: bool, current_user: dict = Depends(get_current_user)):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')

class TokenRequest(BaseModel):
    token: str

@app.post("/token")
async def set_token(token_request: TokenRequest):
    logger.info(f"set_token 엔드포인트 호출됨. TEST_MODE: {TEST_MODE}")
    if TEST_MODE:
        logger.info("테스트 모드 활성화: 테스트 사용자로 초기화")
        await initialize_recognition("test_user")
        return {"message": "테스트 모드: 토큰 수신 및 검증 완료"}
    
    try:
        user = await validate_token(token_request.token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰",
                headers={"WWW-Authenticate": "Bearer"},
            )
        await initialize_recognition(user["id"])
        return {"message": "토큰 수신 및 검증 완료"}
    except Exception as e:
        logger.error(f"토큰 설정 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 처리 중 오류 발생",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def initialize_recognition(user_id: str):
    fetch_family_photos(user_id)
    asyncio.create_task(recognize_periodically(video_frames, user_id))

if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())


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
# #############################################