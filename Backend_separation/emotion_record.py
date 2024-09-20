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


        #non_neutral_emotions = {k: v for k, v in emotion_data.items() if k != 'Neutral'}
        non_neutral_emotions = {k: v for k, v in emotion_data.items() }
        most_frequent_emotion = max(non_neutral_emotions, key=non_neutral_emotions.get)


        return most_frequent_emotion
    except Exception as e:
        print(f"Error while retrieving most frequent emotion: {e}")
        return None

def save_most_emotion_pic(frame, current_emotion, person_name):
    # 최다 감정 사진 경로 설정
    pic_path = get_most_emotion_pic_path(person_name)

    # 현재 감정이 'fear'가 아닌 경우에만 처리
    if current_emotion != 'Fear':
        # 현재 감정이 최다 감정인지 확인
        most_frequent_emotion = get_most_frequent_emotion(person_name)

        # 현재 감정이 최다 감정이거나 새로운 최다 감정이 되었을 때 사진을 저장
        if current_emotion == most_frequent_emotion:
            # 현재 감정이 이미 최다 감정인 경우에도 사진을 저장
            cv2.imwrite(pic_path, frame)
            print(f"Updated most emotion picture for {person_name} with emotion: {current_emotion}")

        elif current_emotion != most_frequent_emotion:
            # 현재 감정이 최다 감정으로 바뀌었을 경우에도 사진을 저장
            cv2.imwrite(pic_path, frame)
            print(f"Updated most emotion picture for {person_name}, new most frequent emotion: {current_emotion}")


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