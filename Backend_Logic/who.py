import cv2
import numpy as np
from deepface import DeepFace
import os
import re


# 등록된 얼굴 목록을 폴더에서 자동으로 불러오기
def load_registered_faces(folder_path):
    registered_faces = []
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):  # 이미지 파일 형식
            registered_faces.append(os.path.join(folder_path, filename))
    return registered_faces


# 파일 이름에서 닉네임 추출하는 함수
def get_nickname_from_filename(filename):
    base_name = os.path.splitext(os.path.basename(filename))[0]  # 확장자 제거
    # 괄호와 그 안의 내용을 제거
    nickname = re.sub(r'\s*\(.*?\)', '', base_name)
    return nickname.strip()  # 공백 제거


# DNN 얼굴 감지 모델 로드
model = cv2.dnn.readNetFromCaffe(
    "models/deploy.prototxt",  # Caffe 모델의 구조 파일
    "models/res10_300x300_ssd_iter_140000.caffemodel"  # Caffe 모델의 가중치 파일
)


# DNN 얼굴 감지 함수
def detect_faces(frame):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    model.setInput(blob)
    detections = model.forward()

    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # 신뢰도 기준
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            faces.append((startX, startY, endX - startX, endY - startY))  # (x, y, w, h)

    return faces


# 등록된 얼굴 로드
registered_faces = load_registered_faces('faces')  # 'faces' 폴더 경로

# 비디오 스트리밍 시작
cap = cv2.VideoCapture(0)  # 0은 기본 카메라를 의미

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = detect_faces(frame)

    for (x, y, w, h) in faces:
        face_image = frame[y:y + h, x:x + w]

        # 얼굴 인식
        try:
            result = DeepFace.find(face_image, db_path='faces', model_name='VGG-Face', enforce_detection=False)

            # 유사도 기준 설정
            threshold = 0.4  # 유사도 기준 거리
            filtered_results = [res for res in result if res['distance'].values[0] < threshold]

            if len(filtered_results) > 0:
                # 등록된 얼굴이 발견된 경우
                matched_face_path = filtered_results[0]['identity'].values[0]  # 첫 번째 열에서 경로 가져오기
                distance = filtered_results[0]['distance'].values[0]  # 첫 번째 열에서 거리 가져오기
                nickname = get_nickname_from_filename(matched_face_path)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Detected: {nickname} ({distance:.2f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        except Exception as e:
            print("Error in face recognition:", e)

    cv2.imshow('Video Stream', frame)

    # 'q'를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
