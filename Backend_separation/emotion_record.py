import os
import json
from datetime import datetime
import cv2
from dateutil.utils import today

from emotion_video import delete_old_videos
def get_emotion_file_today(person_name):
    base_dir = os.path.abspath("../Backend_separation/emotions")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, f"emotion_today_{person_name}.json")

def save_emotion_result(person_name, emotion):
    if emotion == 'Neutral':
        return

    file_path = get_emotion_file_today(person_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
    else:
        emotion_data = initialize_emotion_data()

    # 감정 데이터의 키를 소문자로 맞춘 후, 해당 감정 값을 증가
    emotion = emotion.capitalize()
    if emotion in emotion_data:
        emotion_data[emotion] += 1

    with open(file_path, 'w') as file:
        json.dump(emotion_data, file, indent=4)
    print(f"Emotion data saved to {file_path}")

def get_most_frequent_emotion(person_name):
    try:
        emotion_file_path = get_emotion_file_today(person_name)
        with open(emotion_file_path, 'r') as f:
            emotion_data = json.load(f)

        # 'Neutral'을 제외하고 최다 감정을 찾음
        non_neutral_emotions = {k: v for k, v in emotion_data.items() if k != 'Neutral'}
        most_frequent_emotion = max(non_neutral_emotions, key=non_neutral_emotions.get)

        return most_frequent_emotion
    except Exception as e:
        print(f"Error while retrieving most frequent emotion: {e}")
        return None

def save_most_emotion_pic(frame, emotion, person_name):
    if emotion != 'fear':
        path = get_most_emotion_pic_path(person_name)
        cv2.imwrite(path, frame)
        print(f"Saved most emotion picture for {person_name}: {path}")


def get_most_emotion_pic_path(person_name):
    base_dir = os.path.abspath("../Backend_separation/emotions")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, f"most_emotion_pic_{person_name}.jpg")

def initialize_emotion_data():
    return {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}

def reset_emotion_file():
    file_path = get_emotion_file_today()
    with open(file_path, 'w') as file:
        json.dump(initialize_emotion_data(), file)
    print(f"{file_path} has been reset.")

def manage_daily_files():
    today = datetime.today().strftime('%Y-%m-%d') # 오늘 날짜
    file_path = get_emotion_file_today()

    # 파일의 최종 수정 날짜를 확인하여 하루가 지났는지 확인
    if os.path.exists(file_path):
        last_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if last_modified_time.strftime('%Y-%m-%d') != today:
            # 감정 데이터 초기화
            reset_emotion_file()

    # 이전 하이라이트 영상 삭제
    delete_old_videos(os.path.dirname(file_path), days=2)