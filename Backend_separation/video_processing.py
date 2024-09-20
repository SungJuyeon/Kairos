# video_processing.py
# 비디오 프레임 처리 관련 로직을 포함하는 파일

import asyncio
import logging

import cv2
import numpy as np

from face_recognition import detect_faces, draw_faces
from mqtt_client import video_frames
import time

logger = logging.getLogger(__name__)


async def generate_frames():
    while True:
        if len(video_frames) > 0:
            frame = video_frames[-1]

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 변환된 프레임을 JPEG 형식으로 인코딩
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        await asyncio.sleep(0.1)  # 프레임을 가져오는 간격 조절


async def video_frame_generator(face=True):
    while True:
        if len(video_frames) > 0:
            frame = video_frames[-1]

            if frame is None or not isinstance(frame, np.ndarray):
                logging.error("Invalid frame received.")
                await asyncio.sleep(0.1)  # 잠깐 대기 후 다음 루프 실행
                continue

            if face:
                detect_faces(frame)  # 동기 호출
                frame = draw_faces(frame)  # 동기 호출

            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            await asyncio.sleep(0.1)
        else:
            logging.warning("No frames available, sleeping...")
            await asyncio.sleep(0.1)


# async def video_frame_updater():
#     logger.info("비디오 프레임 업데이터 시작")
#     while True:
#         try:
#             if len(video_frames) > 0:
#                 current_frame = video_frames[0]
#                 await asyncio.to_thread(detect_faces, current_frame)
#                 await asyncio.to_thread(recognize_emotion, current_frame)
#                 await asyncio.to_thread(recognize_faces, current_frame)
#             await asyncio.sleep(1)
#         except Exception as e:
#             logger.error(f"Error processing video frame: {e}")
#             await asyncio.sleep(0.05)
