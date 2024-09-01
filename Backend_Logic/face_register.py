import cv2
import numpy as np
from scipy.ndimage import zoom
from compare_faces import compare_faces

# 얼굴을 감지하는 함수
def detect_face(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # 이미지를 RGB로 처리
    detected_faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48),
                                                   flags=cv2.CASCADE_SCALE_IMAGE)
    coord = []
    for (x, y, w, h) in detected_faces:
        if w > 100:
            coord.append([x, y, w, h])
    return frame, detected_faces, coord

# 얼굴 특징을 추출하는 함수
def extract_face_features(frame, detected_faces, coord, offset_coefficients=(0.075, 0.05)):
    new_face = []
    for det in detected_faces:
        x, y, w, h = det
        horizontal_offset = int(np.floor(offset_coefficients[0] * w))
        vertical_offset = int(np.floor(offset_coefficients[1] * h))
        extracted_face = frame[y + vertical_offset:y + h, x + horizontal_offset:x - horizontal_offset + w]
        new_extracted_face = cv2.resize(extracted_face, (48, 48))  # 48x48로 리사이즈
        new_extracted_face = new_extracted_face.astype(np.float32) / 255.0  # 0-1 범위로 스케일 조정
        new_face.append(new_extracted_face)
    return new_face
