import cv2
import numpy as np
from scipy.ndimage import zoom
from compare_faces import compare_faces

def detect_face(frame):
    # 얼굴 감지 모델 초기화 (예: Haar Cascade)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    detected_faces = []
    coord = []

    for (x, y, w, h) in faces:
        detected_faces.append(gray[y:y+h, x:x+w])
        coord.append((x, y, w, h))
    print(f"Faces: {faces}, Coords: {coord}")
    return gray, detected_faces, coord


def extract_face_features(gray, detected_faces, coord):
    face_features = []

    for (x, y, w, h) in coord:
        face = detected_faces[coord.index((x, y, w, h))]
        face_resized = cv2.resize(face, (48, 48))

        # 이미지가 단일 채널인 경우를 처리
        if len(face_resized.shape) == 2:  # 그레이스케일 이미지
            face_resized = cv2.cvtColor(face_resized, cv2.COLOR_GRAY2RGB)

        face_features.append(face_resized)

    return face_features

