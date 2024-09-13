# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

import asyncio
import logging
import os, json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from typing import List
from emotion_record import get_most_emotion_pic_path, manage_daily_files
from face_recognition import recognize_periodically
from video_processing import generate_frames, video_frame_generator
from mqtt_client import setup_mqtt, distance_data, move, speed, video_frames

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 경로 설정
EMOTION_DATA_DIR = "../Backend_separation/emotions"
MOST_EMOTION_PIC_PATH = os.path.join(EMOTION_DATA_DIR, "most_emotion_pic.jpg")
HIGHLIGHT_VIDEOS_DIR = Path("D:/Users/Downloads/Kairos/Backend_separation/emotions/highlight")
STATIC_DIR = Path("D:/Users/Downloads/Kairos/Backend_separation/emotions")

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요에 따라 특정 도메인으로 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await setup_mqtt()
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
    return {"distance": distance_data}


@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/video_feed/{face}")
async def get_video_feed(face: bool):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')

#최다 감정 사진
@app.get("/most_emotion_pic")
async def get_most_emotion_pic():
    if os.path.exists(MOST_EMOTION_PIC_PATH):
        return FileResponse(MOST_EMOTION_PIC_PATH)
    else:
        raise HTTPException(status_code=404, detail="Most emotion picture not found")

#최다 감정
@app.get("/most_emotion")
async def get_most_emotion():
    file_path = os.path.join(EMOTION_DATA_DIR, "emotion_today.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
        if emotion_data and any(emotion_data.values()):
            most_frequent_emotion, count = max(emotion_data.items(), key=lambda x: x[1])
            return {"emotion": most_frequent_emotion, "count": count}
        else:
            return {"emotion": "No emotion data available", "count": 0}
    else:
        raise HTTPException(status_code=404, detail="Emotion data file not found")

#하이라이트 영상 다운로드
@app.get("/video/{filename}")
async def get_video(filename: str):
    video_path = os.path.join(HIGHLIGHT_VIDEOS_DIR, filename)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    else:
        raise HTTPException(status_code=404, detail="Video not found")

#하이라이트 영상 이름 목록 보기
@app.get("/highlight")
async def get_highlight_videos(request: Request):
    if HIGHLIGHT_VIDEOS_DIR.exists():
        video_files = [f.name for f in HIGHLIGHT_VIDEOS_DIR.iterdir() if f.suffix == '.avi']
        if video_files:
            return JSONResponse(content={video_files})
        else:
            return JSONResponse(content={"detail": "No highlight videos available"}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Highlight videos directory not found")

if __name__ == "__main__":
    manage_daily_files()
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())