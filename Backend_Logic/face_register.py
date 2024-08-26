import cv2
import numpy as np
from scipy.ndimage import zoom
from compare_faces import compare_faces

# 얼굴을 인식하는 함수
def recognize_face(detected_face, registered_face, registered_name):
    if registered_face is None:
        return None
    distance = compare_faces(detected_face, registered_face)
    if distance < 0.4:
        return registered_name
    return None

# 얼굴을 감지하는 함수
def detect_face(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48),
                                                   flags=cv2.CASCADE_SCALE_IMAGE)
    coord = []
    for (x, y, w, h) in detected_faces:
        if w > 100:
            coord.append([x, y, w, h])
    return gray, detected_faces, coord

# 얼굴 특징을 추출하는 함수
def extract_face_features(gray, detected_faces, coord, offset_coefficients=(0.075, 0.05)):
    new_face = []
    for det in detected_faces:
        x, y, w, h = det
        horizontal_offset = int(np.floor(offset_coefficients[0] * w))
        vertical_offset = int(np.floor(offset_coefficients[1] * h))
        extracted_face = gray[y + vertical_offset:y + h, x + horizontal_offset:x - horizontal_offset + w]
        new_extracted_face = zoom(extracted_face, (48 / extracted_face.shape[0], 48 / extracted_face.shape[1]))
        new_extracted_face = new_extracted_face.astype(np.float32) / new_extracted_face.max()
        new_face.append(new_extracted_face)
    return new_face
