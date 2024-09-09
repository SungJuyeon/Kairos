# video_processing.py
# 비디오 프레임 처리 관련 로직을 포함하는 파일

import asyncio
import cv2
from Backend_Logic.FaceRecognotion import FaceRecognition
import logging

logger = logging.getLogger(__name__)

# 상태 변수
video_frames = []
MAX_VIDEO_FRAMES = 5

# 얼굴 인식기 인스턴스 생성
face_recognition = FaceRecognition(
    registered_faces_folder='faces',
    model_prototxt='models/deploy.prototxt',
    model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
)


async def video_frame_updater():
    global video_frames
    logger.info("비디오 프레임 업데이터 시작")
    while True:
        try:
            if len(video_frames) > 0:
                current_frame = video_frames[0]
                await asyncio.to_thread(face_recognition.detect_faces, current_frame)
                await asyncio.to_thread(face_recognition.recognize_emotion, current_frame)
                await asyncio.to_thread(face_recognition.recognize_faces, current_frame)
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.05)


async def video_frame_generator(face_on=True):
    global video_frames
    while True:
        try:
            if len(video_frames) > 0:
                frame = video_frames[0]
                if face_on:
                    face_recognition.draw_faces(frame)

                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.1)
