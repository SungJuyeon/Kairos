import logging
import cv2
import numpy as np
from deepface import DeepFace
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
            result = DeepFace.find(face_image, db_path='faces', model_name='VGG-Face', enforce_detection=False)

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
                last_detected_emotions.append(emotion_result[0]['dominant_emotion'])
                last_detected_emotion_scores.append(emotion_result[0]['emotion'])
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
        return

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


def get_nickname_from_filename(filename):
    base_name = filename.split('/')[-1]  # 파일 경로에서 파일 이름만 추출
    name_part = base_name.split('.')[0]  # 확장자 제거
    name_part = name_part.split('(')[0].strip()  # 괄호 앞부분을 가져옴
    return name_part


async def recognize_periodically(frame_queue):
    logging.error("얼굴 인식 업데이트 시작")
    while True:
        if not frame_queue.empty():
            frame = await frame_queue.get()

            # 프레임 유효성 검사
            if frame is None or frame.size == 0:
                logging.error("받은 프레임이 유효하지 않습니다.")  # 유효하지 않은 프레임 로그
                await asyncio.sleep(1)  # 대기 후 계속 진행
                continue

            await recognize_faces(frame)
            await recognize_emotion(frame)

        else:
            logging.info("프레임 큐가 비어 있습니다.")  # 큐가 비어 있는 경우 로그
            await asyncio.sleep(3)
        await asyncio.sleep(2)


frame_queue = asyncio.Queue()


async def show_frame(frame):
    """프레임을 화면에 표시하는 함수."""
    cv2.imshow("Face Recognition", frame)
    await asyncio.sleep(0.001)  # 짧은 대기


async def video_generator_face_recognition(frame):
    await frame_queue.put(frame)
    if frame_queue.qsize() > 5:
        await frame_queue.get()

    detect_faces(frame)  # 얼굴 감지
    draw_faces(frame)  # 얼굴 및 감정 정보 그리기


# 나머지 코드...

async def main():
    asyncio.create_task(recognize_periodically(frame_queue))

    cap = cv2.VideoCapture(0)  # 웹캠에서 비디오 캡처
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("프레임을 읽는 데 실패했습니다.")  # 프레임 읽기 실패 로그
            break
        await video_generator_face_recognition(frame)
        # 프레임을 비동기적으로 표시
        await show_frame(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
            break

    cap.release()
    cv2.destroyAllWindows()


# 메인 함수 실행
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
