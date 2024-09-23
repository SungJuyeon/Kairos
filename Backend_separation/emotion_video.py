import os
import datetime
import cv2
import json

HIGHLIGHT_DIR = os.path.abspath("../Backend_separation/emotions/highlight")

highlight_frames = []
highlight_start_time = None

def save_frames_to_video(filename, frames):
    # Save highlight video
    if not frames:
        print("No frames to save.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # 5 = frame_rate
    out = cv2.VideoWriter(filename, fourcc, 5, (frames[0].shape[1], frames[0].shape[0]))

    for frame in frames:
        out.write(frame)

    out.release()
    print(f"Video saved: {filename}")

def generate_video_filename(detected_person_name):
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    file_index = 1

    filename = os.path.join(HIGHLIGHT_DIR, f"{today_date}_{detected_person_name}_{file_index}.avi")

    while os.path.isfile(filename):
        file_index += 1
        filename = os.path.join(HIGHLIGHT_DIR, f"{today_date}_{detected_person_name}_{file_index}.avi")

    return filename

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
