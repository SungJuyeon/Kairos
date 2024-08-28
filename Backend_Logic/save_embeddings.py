import os
import pandas as pd
from deepface import DeepFace

# 등록된 얼굴 목록을 폴더에서 자동으로 불러오기
def load_registered_faces(folder_path):
    registered_faces = []
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):  # 이미지 파일 형식
            registered_faces.append(os.path.join(folder_path, filename))
    return registered_faces

# 얼굴 임베딩을 계산하고 저장하는 함수
def save_face_embeddings(folder_path, output_file):
    registered_faces = load_registered_faces(folder_path)
    embeddings = []

    for face_path in registered_faces:
        try:
            # 얼굴 임베딩 계산
            embedding = DeepFace.represent(face_path, model_name='VGG-Face', enforce_detection=False)[0]
            embeddings.append({
                "identity": face_path,
                "embedding": embedding["embedding"]
            })
        except Exception as e:
            print(f"Error processing {face_path}: {e}")

    # DataFrame으로 변환하고 CSV 파일로 저장
    df = pd.DataFrame(embeddings)
    output_path = os.path.join(folder_path, output_file)  # faces 폴더 안에 파일 경로 지정
    df.to_csv(output_path, index=False)

# 사용 예
if __name__ == "__main__":
    save_face_embeddings('faces', 'face_embeddings.csv')
