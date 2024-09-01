import os
import json
from datetime import datetime

# 감정 파일 경로 설정 함수 (오늘의 감정 파일 경로 설정)
def get_emotion_file_today():
    base_dir = os.path.abspath("../Backend_Logic/emotions")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, "emotion_today.json")

# 감정 데이터 초기화 함수
def initialize_emotion_data():
    return {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}

# 감정 파일 초기화 함수 (하루가 끝나면 호출)
def reset_emotion_file():
    file_path = get_emotion_file_today()
    with open(file_path, 'w') as file:
        json.dump(initialize_emotion_data(), file)
    print(f"{file_path} has been reset.")

# 감정 결과 저장 함수
def save_emotion_result(emotion):
    file_path = get_emotion_file_today()

    # 기존 데이터 로드
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
    else:
        emotion_data = initialize_emotion_data()

    # 감정 카운트 증가
    if emotion in emotion_data:
        emotion_data[emotion] += 1

    # 데이터 저장
    with open(file_path, 'w') as file:
        json.dump(emotion_data, file)
    print(f"Emotion data saved to {file_path}")

# 감정 발생 횟수를 기록하는 함수
def record_emotion(emotion):
    save_emotion_result(emotion)

# 가장 빈번한 감정을 조회하는 함수
def get_most_frequent_emotion():
    file_path = get_emotion_file_today()
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
        if emotion_data and any(emotion_data.values()):
            most_frequent_emotion = max(emotion_data.items(), key=lambda x: x[1])
            return most_frequent_emotion
        else:
            return ("No emotion data available", 0)
    else:
        return ("No emotion data available", 0)

# 감정 랭킹을 조회하는 함수
def get_emotion_ranking():
    file_path = get_emotion_file_today()
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
        sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_emotions
    else:
        return []

# 하루가 끝나면 오늘의 감정 데이터 파일을 초기화
def manage_daily_files():
    today = datetime.today().strftime('%Y-%m-%d')
    file_path = get_emotion_file_today()

    # 오늘 날짜의 파일이 존재하지 않으면 초기화 (새로운 날이 시작됨을 의미)
    if not os.path.exists(file_path):
        reset_emotion_file()

    # 현재 날짜와 감정 파일 수정 날짜를 비교
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
    if file_mtime != today:
        reset_emotion_file()