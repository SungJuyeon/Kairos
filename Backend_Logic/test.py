import cv2
from deepface import DeepFace
import os
import re
import numpy as np
import tempfile

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
    nickname = re.sub(r'\s*\(.*?\)', '', base_name)
    return nickname.strip()  # 공백 제거

# 얼굴 감지 함수
def detect_faces(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
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

        # 임시 파일에 얼굴 이미지 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_face_path = temp_file.name
            cv2.imwrite(temp_face_path, face_image)

        match_found = False

        for registered_face in registered_faces:
            try:
                # DeepFace.verify를 사용하여 비교
                result = DeepFace.verify(temp_face_path, registered_face, model_name='VGG-Face')
                if result['verified']:
                    nickname = get_nickname_from_filename(registered_face)  # 닉네임 추출
                    match_found = True

                    # 얼굴 주변에 사각형 그리기 및 닉네임 표시
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, nickname, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    break

            except Exception as e:
                print("Error in face recognition:", e)

        if not match_found:
            # 등록된 얼굴이 발견되지 않은 경우
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 빨간색 사각형
            cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # 임시 파일 삭제
        os.remove(temp_face_path)

    cv2.imshow('Video Stream', frame)

    # 'q'를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
