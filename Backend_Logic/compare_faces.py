import cv2
import numpy as np
import face_recognition

def compare_faces(face1, face2):
    # 얼굴 이미지에서 얼굴 특징 추출
    face1_encoding = face_recognition.face_encodings(face1)
    face2_encoding = face_recognition.face_encodings(face2)

    if len(face1_encoding) == 0 or len(face2_encoding) == 0:
        print("One or both faces are not detected.")
        return False, None  # 얼굴이 감지되지 않으면 비교 불가

    face1_encoding = face1_encoding[0]
    face2_encoding = face2_encoding[0]

    # 두 얼굴 간의 거리 계산
    distance = np.linalg.norm(face1_encoding - face2_encoding)
    print(f"Face1 encoding: {face1_encoding}")
    print(f"Face2 encoding: {face2_encoding}")
    print(f"Distance: {distance}")
    return True, distance

def get_similarity_percentage(face1, face2):
    match, distance = compare_faces(face1, face2)
    if not match:
        return 0.0  # 얼굴이 감지되지 않으면 유사도 0%
    similarity_percentage = max(0, (1 - distance) * 100)
    return similarity_percentage


def get_similarity_percentage(face1, face2):
    match, distance = compare_faces(face1, face2)
    if not match:
        return 0.0  # 얼굴이 감지되지 않으면 유사도 0%
    similarity_percentage = max(0, (1 - distance) * 100)
    return similarity_percentage
