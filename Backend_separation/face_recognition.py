import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from emotion_record import get_most_frequent_emotion, save_emotion_result, save_most_emotion_pic
from mqtt_client import video_frames
import boto3
import cv2
import numpy as np
from deepface import DeepFace

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 전역 변수 초기화
current_dir = os.path.dirname(os.path.abspath(__file__))
prototxt_path = os.path.join(current_dir, 'models', 'deploy.prototxt')
model_path = os.path.join(current_dir, 'models', 'res10_300x300_ssd_iter_140000.caffemodel')
faces_dir = os.path.join(current_dir, 'faces')  # faces 폴더의 절대 경로

model = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
last_detected_nicknames = []
last_detected_distances = []
last_detected_rectangles = []
last_face_positions = []
last_detected_emotions = []
last_detected_emotion_scores = []
faces = []
executor = ThreadPoolExecutor(max_workers=4)


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


async def recognize_faces(frame):
    global last_detected_nicknames, last_detected_distances, last_detected_rectangles, last_face_positions
    if last_face_positions is None:
        last_detected_nicknames = ["unknown"]
        last_detected_distances = [None]
        last_detected_rectangles = []
        return

    last_detected_nicknames.clear()
    last_detected_distances.clear()
    last_detected_rectangles.clear()

    for idx, (x, y, w, h) in enumerate(last_face_positions):
        face_image = frame[y:y + h, x:x + w]

        try:
            result = DeepFace.find(face_image, db_path=faces_dir, model_name='VGG-Face', enforce_detection=False)

            if result and len(result) > 0:
                threshold = 0.4
                filtered_results = [res for res in result if res['distance'].values[0] < threshold]

                if filtered_results:
                    matched_face_path = filtered_results[0]['identity'].values[0]
                    last_detected_distances.append(filtered_results[0]['distance'].values[0])
                    last_detected_nicknames.append(get_nickname_from_filename(matched_face_path))
                    last_detected_rectangles.append(last_face_positions[idx])  # 초록색 사각형 정보 추가
                else:
                    last_detected_nicknames.append("unknown")
                    last_detected_distances.append(None)
                    last_detected_rectangles.append(None)
            else:
                last_detected_nicknames.append("unknown")
                last_detected_distances.append(None)
                last_detected_rectangles.append(None)

        except Exception as e:
            print("Error in face recognition:", e)
            last_detected_nicknames.append("unknown")
            last_detected_distances.append(None)
            last_detected_rectangles.append(None)


async def recognize_emotion(frame):
    global last_detected_emotions, last_detected_emotion_scores, last_face_positions
    detected_person_name = last_detected_nicknames[0] if last_detected_nicknames else "unknown"

    if detected_person_name == "unknown":
        last_detected_emotions = ["unknown"]
        last_detected_emotion_scores = [{}]
        return

    most_frequent_emotion = get_most_frequent_emotion(detected_person_name)

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
                current_emotion = emotion_result[0]['dominant_emotion']
                last_detected_emotions.append(current_emotion)
                last_detected_emotion_scores.append(emotion_result[0]['emotion'])


                if current_emotion != 'fear' and detected_person_name != "unknown":
                    #emotion_today_{detected_person_name}.json 으로 감정 수치 저장
                    save_emotion_result(detected_person_name, current_emotion)
                    #최다 감정 사진 저장
                    new_most_frequent_emotion = get_most_frequent_emotion(detected_person_name)
                    if new_most_frequent_emotion != most_frequent_emotion:
                        save_most_emotion_pic(frame, new_most_frequent_emotion, detected_person_name)
                        logging.info(f"Updated most emotion photo for {detected_person_name} with emotion: {new_most_frequent_emotion}")

            else:
                last_detected_emotions.append("unknown")
                last_detected_emotion_scores.append({})

        except Exception as e:
            print("Error in emotion recognition:", e)
            last_detected_emotions.append("unknown")
            last_detected_emotion_scores.append({})


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


async def recognize_periodically():
    logging.info("얼굴 인식 업데이트 시작")
    while True:
        try:
            frame = video_frames[-1]
            detect_faces(frame)
            await recognize_faces(frame)
            await recognize_emotion(frame)
            await create_video_highlight()
            logging.info("인식 완료")
        except IndexError:
            logging.info("리스트가 비어 있습니다.")
        finally:
            await asyncio.sleep(2)



is_saving_video = False  # 비디오 저장 중인지 여부를 나타내는 플래그


async def create_video_highlight():
    global is_saving_video  # 플래그를 전역으로 사용


    current_emotions = last_detected_emotions
    current_emotion_scores = last_detected_emotion_scores
    current_nickname = last_detected_nicknames

    if current_nickname != "unkown" and current_emotions and not is_saving_video:  # 비디오 저장 중이 아닐 때만 실행
        for idx, emotion in enumerate(current_emotions):
            score = current_emotion_scores[idx].get(emotion, 0)
            if emotion != "neutral" and score >= 0.4:
                asyncio.create_task(save_video())


async def save_video(fps=10, seconds=20):
    logging.info("비디오 저장 시작##########################################")
    global is_saving_video
    is_saving_video = True  # 비디오 저장 시작
    if not video_frames :
        logging.info("비디오 프레임이 없습니다.")
        is_saving_video = False
        return

    detected_person_name = last_detected_nicknames[0] if last_detected_nicknames else "unknown"
    detected_emotion = last_detected_emotions[0] if last_detected_emotions else "unknown"
    video_file_name = f'{detected_person_name}_{detected_emotion}_{time.strftime("%Y%m%d_%H%M%S")}.avi'
    first_frame = video_frames[0]
    h, w = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(video_file_name, fourcc, fps, (w, h))

    start_time = time.time()
    end_time = start_time + seconds

    while time.time() < end_time:
        if video_frames:
            frame = video_frames[-1]  # 가장 최근 프레임 사용
            out.write(frame)
        await asyncio.sleep(1 / fps)  # fps에 맞춰 대기

    is_saving_video = False

    out.release()  # 비디오 파일 닫기
    logging.info("비디오 저장 완료##########################################")