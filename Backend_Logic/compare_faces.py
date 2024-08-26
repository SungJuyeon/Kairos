import numpy as np
from scipy.spatial.distance import cosine
#import face_recognition
def preprocess_face(face):
    # 정규화: 0-255 범위를 0-1 범위로 변환
    return face.astype(np.float32) / 255.0

# 얼굴 유사성을 비교하는 함수 (코사인 유사도 사용)
def compare_faces(face1, face2):
    if face1.shape != face2.shape:
        raise ValueError(f"Face shapes do not match: {face1.shape} vs {face2.shape}")

    # 전처리: 정규화
    face1 = preprocess_face(face1)
    face2 = preprocess_face(face2)

    # Flatten the faces
    face1_flat = face1.flatten()
    face2_flat = face2.flatten()

    print(f"Face1 flattened shape: {face1_flat.shape}")
    print(f"Face2 flattened shape: {face2_flat.shape}")
    print(f"Face1 data: {face1_flat[:10]}...")  # Print first 10 values for brevity
    print(f"Face2 data: {face2_flat[:10]}...")  # Print first 10 values for brevity

    distance = cosine(face1_flat, face2_flat)
    similarity = 1 - distance  # 코사인 유사도는 거리를 1에서 뺀 값

    print(f"Cosine distance: {distance}")
    print(f"Similarity: {similarity}")

    return similarity

# 유사도를 퍼센트로 변환하는 함수
def get_similarity_percentage(face1, face2):
    similarity = compare_faces(face1, face2)
    return similarity * 100  # Convert to percentage
