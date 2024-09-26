import asyncio
import logging
import os
import json
from typing import Dict, List
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Header, WebSocket
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse, FileResponse
from face_recognition import recognize_periodically
from follow import follow, generate_video_frames
import hand_gesture_recognition
from hand_gesture_recognition import recognize_hand_gesture_periodically
from video_processing import generate_frames, video_frame_generator
from mqtt_client import home_control, setup_mqtt, distance_data, move, speed, text_to_audio, video_frames
from db_face_loader import load_faces_from_db
from s3_uploader import list_s3_videos
from calendar_app import get_all_schedules, add_schedules, delete_schedule, Schedule
from emotion_record import get_most_emotion_pic_path, get_most_frequent_emotion
from face_image_db import current_userId, fetch_family_photos
from message_server import handle_connection, fetch_user_id_by_username

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    #get_face_recognition()
    load_faces_from_db()  # 얼굴 이미지 로드
    #get_hand_gesture_recognition()
        
face_recognition_task = None
@app.get("/face_recognition")
async def get_face_recognition():
    global face_recognition_task
    face_recognition_task = asyncio.create_task(recognize_periodically())
    return {"message": "얼굴 인식 태스크가 시작되었습니다."}

@app.get("/face_recognition_stop")
async def get_face_recognition_stop():
    global face_recognition_task
    face_recognition_task.cancel()
    return {"message": "얼굴 인식 태스크가 종료되었습니다."}

hand_gesture_recognition_task = None
@app.get("/hand_gesture_recognition")
async def get_hand_gesture_recognition():
    global hand_gesture_recognition_task
    hand_gesture_recognition.init()
    hand_gesture_recognition_task = asyncio.create_task(recognize_hand_gesture_periodically())
    return {"message": "손동작 인식 태스크가 시작되었습니다."}

@app.get("/hand_gesture_recognition_stop")
async def get_hand_gesture_recognition_stop():
    global hand_gesture_recognition_task
    hand_gesture_recognition_task.cancel()
    return {"message": "손동작 인식 태스크가 종료되었습니다."}



@app.post("/move/{direction}")
async def post_move(direction: str):
    await move(direction)

@app.post("/speed/{action}")
async def post_speed(action: str):
    await speed(action)
    

@app.get("/distance")
async def get_distance():
    logger.info("get_distance 엔드포인트 호출됨.")
    return {"distance": distance_data}

@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/video_feed/{face}/{hand}")
async def get_video_feed(face: bool, hand: bool):
    return StreamingResponse(video_frame_generator(face, hand),
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

@app.get("/calendar", response_model=List[Dict])
async def calendar(token: str = Header(...)):
    schedules = get_all_schedules(token)
    return {"schedules": schedules}

@app.get("/schedules", response_model=List[Dict]) 
def read_schedules(token: str):
    return get_all_schedules(token)

@app.post("/schedules/add")
async def add_schedule_endpoint(schedule: Schedule, token: str = Header(...)):
    return add_schedules(schedule, token)

@app.delete("/schedules/{schedule_id}")
async def delete_schedule_endpoint(schedule_id: int, token: str = Header(...)):
    return delete_schedule(schedule_id, token)

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

@app.get("/messages/{username}")
async def get_messages(username: str):
    user_id = fetch_user_id_by_username(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    message_log = f"{user_id}_messages.json"

    if not os.path.exists(message_log):
        return {"messages": []}

    with open(message_log, "r", encoding="utf-8") as file:
        try:
            messages = json.load(file)
        except json.JSONDecodeError:
            messages = []
    return {"messages": messages}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await handle_connection(websocket)


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

@app.get("/follow")
async def get_follow():
    asyncio.create_task(follow())
@app.get("/follow_video")
async def get_follow_video():
    return StreamingResponse(generate_video_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/home_control/{device}/{state}")
async def post_home_control(device: str, state: bool):
    await home_control(device, state)
    
@app.get("/text_to_audio/{text}")
async def post_text_to_audio(text: str):
    await text_to_audio(text)

if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
