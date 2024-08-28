import cv2
import numpy as np

import cv2
import numpy as np

def detect_face(image):
    # 얼굴 인식 및 감지
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return gray, [image[y:y+h, x:x+w] for (x, y, w, h) in faces], faces

def extract_face_features(gray_image, detected_faces, coords):
    # 얼굴 영역 추출
    face_features = []
    for (x, y, w, h) in coords:
        face = gray_image[y:y+h, x:x+w]
        face_features.append(cv2.resize(face, (48, 48)))
    return face_features
