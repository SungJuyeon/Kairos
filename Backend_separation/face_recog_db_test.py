import logging
import os
import datetime
import cv2
import numpy as np
from deepface import DeepFace
import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image

from face_image_db import get_faces_from_db
from emotion_video import delete_old_videos

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 전역 변수 초기화
model = cv2.dnn.readNetFromCaffe('models/deploy.prototxt', 'models/res10_300x300_ssd_iter_140000.caffemodel')
last_detected_nicknames = []
last_detected_distances = []
last_detected_rectangles = []
last_face_positions = []
last_detected_emotions = []
last_detected_emotion_scores = []
faces = []
executor = ThreadPoolExecutor(max_workers=4)
highlight_frames = []

def detect_faces(frame):
    global faces, last_face_positions
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    model.setInput(blob)
    detections = model.forward()

    faces.clear()  # 이전 얼굴 정보를 초기화

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.8:  # 신뢰도가 0.8 이상인 경우만 처리
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            faces.append((startX, startY, endX - startX, endY - startY))

    last_face_positions = faces if faces else None  # 얼굴이 감지되지 않은 경우 None으로 설정

def load_image_from_blob(blob_data):
    return Image.open(BytesIO(blob_data))

async def recognize_faces(frame):
    global last_detected_nicknames, last_detected_distances, last_detected_rectangles, last_face_positions

    if last_face_positions is None:
        last_detected_nicknames = ["unknown"]
        last_detected_distances = [None]
        last_detected_rectangles = []
        return

    faces_db = get_faces_from_db()
    faces_db_images = {nickname: load_image_from_blob(photoname) for nickname, photoname in faces_db}

    last_detected_nicknames.clear()
    last_detected_distances.clear()
    last_detected_rectangles.clear()

    for idx, (x, y, w, h) in enumerate(last_face_positions):
        face_image = frame[y:y + h, x:x + w]
        face_pil = Image.fromarray(face_image)

        matched_nickname = "unknown"
        min_distance = float('inf')

        for nickname, db_image in faces_db_images.items():
            result = DeepFace.verify(face_pil, db_image, model_name='VGG-Face', enforce_detection=False)
            if result and result['distance'] < min_distance:
                min_distance = result['distance']
                matched_nickname = nickname

        last_detected_nicknames.append(matched_nickname)
        last_detected_distances.append(min_distance if min_distance < 0.4 else None)
        last_detected_rectangles.append(last_face_positions[idx])


async def recognize_emotion(frame):
    global last_detected_emotions, last_detected_emotion_scores, last_face_positions
    if last_face_positions is None:
        last_detected_emotions = ["unknown"]
        last_detected_emotion_scores = [{}]
        return

    last_detected_emotions.clear()
    last_detected_emotion_scores.clear()

    for (x, y, w, h) in last_face_positions:
        face_image = frame[y:y + h, x:x + w]

        try:
            emotion_result = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False)
            if emotion_result:
                emotion = emotion_result[0]['dominant_emotion']
                last_detected_emotions.append(emotion_result[0]['dominant_emotion'])
                last_detected_emotion_scores.append(emotion_result[0]['emotion'])
                # 감정 결과 저장 (Neutral 제외)
                from Backend_separation.emotion_record import save_emotion_result
                save_emotion_result(emotion)

                # 감정이 90을 넘는 경우 하이라이트 영상 저장
                top_emotion, top_score = max(emotion_result[0]['emotion'].items(), key=lambda x: x[1])
                if top_score > 90 and top_emotion != 'Neutral':
                    highlight_frames.append(frame)

            else:
                last_detected_emotions.append("unknown")
                last_detected_emotion_scores.append({})

        except Exception as e:
            print("Error in emotion recognition:", e)
            last_detected_emotions.append("unknown")
            last_detected_emotion_scores.append({})

    # 감정 사진 저장 (최다 감정 갱신)
    from Backend_separation.emotion_record import get_most_frequent_emotion
    most_frequent_emotion, _ = get_most_frequent_emotion()
    if most_frequent_emotion != 'Neutral':
        if last_detected_emotions:
            current_emotion = last_detected_emotions[-1]
            if current_emotion == most_frequent_emotion:
                from Backend_separation.emotion_record import save_most_emotion_pic
                save_most_emotion_pic(frame, current_emotion)


def draw_faces(frame):
    global last_face_positions, last_detected_nicknames, last_detected_distances, last_detected_emotions, \
        last_detected_emotion_scores
    if last_face_positions is None:
        return frame

    for idx, (x, y, w, h) in enumerate(last_face_positions):
        # 얼굴 감지 사각형 (노란색)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 노란색

        # 감정 정보가 있는지 확인하고 그리기
        if last_detected_emotions and idx < len(last_detected_emotions):
            emotion = last_detected_emotions[idx]
            if emotion:
                scores = last_detected_emotion_scores[idx]
                if scores:
                    sorted_emotions = sorted(scores.items(), key=lambda item: item[1], reverse=True)
                    top_emotion, top_score = sorted_emotions[0]
                    cv2.putText(frame, f"{top_emotion}: {top_score:.2f}%", (x + w + 10, y + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)  # 빨간색

        # 인식된 얼굴에 대해서는 초록색 사각형
        if idx < len(last_detected_nicknames) and last_detected_nicknames[idx] != "unknown":
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색
        nickname = last_detected_nicknames[idx] if idx < len(last_detected_nicknames) else "unknown"
        distance = last_detected_distances[idx] if idx < len(last_detected_distances) else None

        if distance is not None:
            cv2.putText(frame, f"Detected: {nickname} ({distance:.2f})",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            cv2.putText(frame, f"Detected: {nickname}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame


def get_nickname_from_filename(filename):
    base_name = filename.split('/')[-1]  # 파일 경로에서 파일 이름만 추출
    name_part = base_name.split('.')[0]  # 확장자 제거
    name_part = name_part.split('(')[0].strip()  # 괄호 앞부분을 가져옴
    return name_part


async def recognize_periodically(video_frames):
    logging.info("얼굴 인식 업데이트 시작")
    while True:
        try:
            frame = video_frames[-1]
            await recognize_faces(frame)
            await recognize_emotion(frame)

            # 하이라이트 영상 저장
            if highlight_frames:
                from Backend_separation.emotion_video import generate_video_filename
                video_filename = generate_video_filename("highlight")
                from Backend_separation.emotion_video import save_frames_to_video
                save_frames_to_video(video_filename, highlight_frames)
                highlight_frames.clear()

            logging.info("인식 완료")
        except IndexError:
            logging.info("리스트가 비어 있습니다.")
        finally:
            await asyncio.sleep(2)

# 매일 자정에 감정 데이터 파일 초기화
def manage_daily_files():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    from Backend_separation.emotion_record import get_emotion_file_today
    file_path = get_emotion_file_today()
    if os.path.exists(file_path):
        # 감정 데이터 초기화
        from Backend_separation.emotion_record import reset_emotion_file
        reset_emotion_file()

    # 이전 하이라이트 영상 삭제
    delete_old_videos(os.path.dirname(file_path), days=2)