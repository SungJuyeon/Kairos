import cv2
import os
import time
import re
from datetime import datetime


# 비디오 저장 경로 및 파일명 생성 함수
def generate_video_filename():
    base_dir = "unused/videos"  # 비디오 파일 저장 폴더
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)  # 폴더가 없으면 생성

    today = datetime.today().strftime('%Y%m%d')  # 오늘 날짜

    # 오늘 날짜에 해당하는 모든 비디오 파일 이름을 검색
    existing_files = [f for f in os.listdir(base_dir) if f.startswith(today) and f.endswith('.avi')]

    # 파일 이름에서 번호 추출
    max_number = 0
    for filename in existing_files:
        match = re.match(rf"{today}(\d+).avi", filename)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number

    # 다음 번호 생성
    next_number = max_number + 1

    return os.path.join(base_dir, f"{today}{next_number}.avi")  # 비디오 파일 경로, 이름 반환


# 비디오 파일에 프레임을 저장하는 함수
def save_frames_to_video(filename, frames, frame_rate=5):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    height, width, layers = frames[0].shape
    out = cv2.VideoWriter(filename, fourcc, frame_rate, (width, height))

    for frame in frames:
        out.write(frame)

    out.release()


def delete_old_videos(directory, days=2):
    now = datetime.datetime.now()
    for filename in os.listdir(directory):
        if filename.endswith(".avi"):
            try:
                date_part = filename.split('_')[-1].replace('.avi', '')
                video_date = datetime.datetime.strptime(date_part, '%Y-%m-%d')
                if (now - video_date).days >= days:
                    os.remove(os.path.join(directory, filename))
                    print(f"Deleted old video file: {filename}")
            except Exception as e:
                print(f"Error parsing date from filename: {filename}, {e}")
