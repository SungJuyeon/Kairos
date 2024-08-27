import face_recognition
import cv2
import numpy as np

# 얼굴 유사성을 비교하는 함수
def compare_faces(face1, face2):
    try:
        # 이미지를 8비트 그레이스케일 또는 RGB로 변환
        if len(face1.shape) == 2:  # 그레이스케일 이미지일 경우
            face1 = cv2.cvtColor(face1, cv2.COLOR_GRAY2RGB)
        elif face1.shape[2] == 4:  # RGBA 이미지일 경우
            face1 = cv2.cvtColor(face1, cv2.COLOR_RGBA2RGB)

        if len(face2.shape) == 2:  # 그레이스케일 이미지일 경우
            face2 = cv2.cvtColor(face2, cv2.COLOR_GRAY2RGB)
        elif face2.shape[2] == 4:  # RGBA 이미지일 경우
            face2 = cv2.cvtColor(face2, cv2.COLOR_RGBA2RGB)

        # 얼굴 인코딩 얻기
        faceLoc1 = face_recognition.face_locations(face1)
        faceLoc2 = face_recognition.face_locations(face2)

        # 얼굴이 감지되지 않았을 때 처리
        if len(faceLoc1) == 0 or len(faceLoc2) == 0:
            return False, 1.0  # 얼굴이 감지되지 않으면 False와 최대 거리 반환

        encodeFace1 = face_recognition.face_encodings(face1, known_face_locations=faceLoc1)[0]
        encodeFace2 = face_recognition.face_encodings(face2, known_face_locations=faceLoc2)[0]

        # 두 얼굴을 비교하여 유사성 확인
        results = face_recognition.compare_faces([encodeFace1], encodeFace2)
        faceDis = face_recognition.face_distance([encodeFace1], encodeFace2)

        return results[0], faceDis[0]  # 유사성 결과와 거리 반환

    except Exception as e:
        # 인코딩이나 다른 처리 중에 문제가 발생하면 예외 처리
        print(f"Error in compare_faces: {e}")
        return False, 1.0  # 얼굴이 제대로 인식되지 않으면 False와 최대 거리 반환

# 유사도를 퍼센트로 변환하는 함수
def get_similarity_percentage(face1, face2):
    _, faceDis = compare_faces(face1, face2)
    # 거리 값이 작을수록 유사도가 높으므로, 1 - 거리 값으로 유사도를 계산
    similarity_percentage = (1 - faceDis) * 100
    return similarity_percentage
