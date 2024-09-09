# app.py
# FastAPI 서버 및 엔드포인트를 설정하는 파일

import asyncio
import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from mqtt_client import setup_mqtt, distance_data, audio_data, video_frames
from video_processing import video_frame_updater, video_frame_generator

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await setup_mqtt()
    asyncio.create_task(video_frame_updater())

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/distance")
async def get_distance():
    return {"distance": distance_data}

@app.get("/audio_feed")
async def get_audio_feed():
    if not audio_data:
        return {"error": "No audio data available"}

    # WAV 형식으로 변환
    import io
    import wave
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, 'wb') as wf:
        wf.setnchannels(1)  # 모노
        wf.setsampwidth(2)  # 16비트 샘플
        wf.setframerate(44100)  # 샘플링 주파수
        wf.writeframes(b''.join(audio_data))  # 오디오 데이터 추가

    audio_buffer.seek(0)  # 버퍼의 시작으로 이동
    return StreamingResponse(audio_buffer, media_type="audio/wav")

@app.get("/video_feed/{face_on}")
async def get_video_feed(face_on: bool):
    return StreamingResponse(video_frame_generator(face_on),
                             media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
