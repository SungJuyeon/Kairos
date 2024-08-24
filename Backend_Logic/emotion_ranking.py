import os
import json
from datetime import datetime

# 감정 파일 경로를 생성하는 함수
def get_emotion_file():
    base_dir = "../AI/emotions"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    today = datetime.today().strftime('%Y%m%d')  # 오늘 날짜
    return os.path.join(base_dir, f"{today}.json")  # 감정 파일 경로 반환

# 감정 결과 저장 함수
def save_emotion_result(emotion):
    file_path = get_emotion_file()

    # 기존 데이터 로드
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
    else:
        emotion_data = {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}

    # 감정 카운트 증가
    if emotion in emotion_data:
        emotion_data[emotion] += 1

    # 데이터 저장
    with open(file_path, 'w') as file:
        json.dump(emotion_data, file)

# 감정 순위 반환 함수
def get_emotion_ranking():
    file_path = get_emotion_file()

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
        # 감정을 빈도에 따라 내림차순으로 정렬
        sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_emotions
    else:
        return []

