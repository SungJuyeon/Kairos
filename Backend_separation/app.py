# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse

from face_recognition import recognize_periodically
from video_processing import generate_frames, video_frame_generator
from mqtt_client import setup_mqtt, distance_data, move, speed, video_frames, speech_text
from db_face_loader import load_faces_from_db
from s3_uploader import list_s3_videos

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
    """
    S3에 저장된 영상 목록을 반환하는 엔드포인트
    """
    video_list = await list_s3_videos()
    return {"videos": video_list}


@app.get("/speech_text")
async def get_speech_text():
    return {"speech_text": speech_text}


if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
