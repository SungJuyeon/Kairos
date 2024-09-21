# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

import asyncio
import logging
import os
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse, FileResponse

from face_recognition import recognize_periodically
from video_processing import generate_frames, video_frame_generator
from mqtt_client import setup_mqtt, distance_data, move, speed
from db_face_loader import load_faces_from_db
from s3_uploader import list_s3_videos
from calendar_app import get_all_schedules, add_schedule, delete_schedule, Schedule
from emotion_record import get_most_emotion_pic_path, get_most_frequent_emotion
from face_image_db import fetch_family_photos, current_userId

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    asyncio.create_task(recognize_periodically())
    load_faces_from_db()  # 얼굴 이미지 로드

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

@app.post("/load_faces")
async def load_faces():
    try:
        load_faces_from_db()
        return {"message": "얼굴 이미지가 성공적으로 로드되었습니다."}
    except Exception as e:
        logger.error(f"얼굴 이미지 로드 중 오류 발생: {str(e)}")
        return {"error": "얼굴 이미지 로드 중 오류가 발생했습니다.", "details": str(e)}, 500

@app.get("/s3_video_list")
async def get_video_list():
    video_list = await list_s3_videos()
    return {"videos": video_list}

@app.get("/calendar")
def calendar():
    schedules = get_all_schedules()
    return {"schedules": schedules}

@app.delete("/schedules/{schedule_id}")
def delete_schedule_endpoint(schedule_id: int):
    return delete_schedule(schedule_id)

@app.post("/schedules/add")
def add_schedule_endpoint(schedule: Schedule):
    return add_schedule(schedule)

@app.get("/most_emotion")
async def most_emotion(token: str = Header(...)):
    user_id = await current_userId(token)  # 비동기 함수 호출로 user_id 추출
    logging.info(user_id)
    most_frequent_emotion = get_most_frequent_emotion(user_id)  # user_id로 감정 데이터 가져오기
    if most_frequent_emotion is None:
        raise HTTPException(status_code=404, detail="Emotion data not found.")
    return {"most_frequent_emotion": most_frequent_emotion}

@app.get("/most_emotion_pic")
async def most_emotion_pic(token: str = Header(...)):
    user_id = await current_userId(token)  # 비동기 함수 호출로 user_id 추출
    pic_path = get_most_emotion_pic_path(user_id)  # user_id로 사진 경로 가져오기
    if not os.path.exists(pic_path):
        raise HTTPException(status_code=404, detail="Emotion picture not found.")

    return FileResponse(pic_path, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
