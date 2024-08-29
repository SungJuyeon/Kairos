import os
import datetime
import cv2
import json

def save_frames_to_video(filename, frames):
    #하이라이트 영상 저장
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # 5 = frame_rate
    out = cv2.VideoWriter(filename, fourcc, 5, (frames[0].shape[1], frames[0].shape[0]))

    for frame in frames:
        out.write(frame)

    out.release()

    metadata_filename = f"{filename}.json"
    creation_time = datetime.datetime.now().isoformat()
    metadata = {"creation_time": creation_time}

    with open(metadata_filename, 'w') as f:
        json.dump(metadata, f)

def generate_video_filename(detected_person_name):
    today_date = datetime.datetime.now().strfttime('%Y-%m-%d')
    file_index = 1
    while os.path.isfile(f"{today_date}_{detected_person_name}_{file_index}.avi"):
        file_index += 1
    filename = f"{today_date}_{detected_person_name}_{file_index}.avi"
    return filename

def delete_old_videos(directory, days=2):
    now = datetime.datetime.now()
    for filename in os.listdir(directory):
        if filename.endswith(".avi"):
            metadata_filename = f"{filename}.json"
            if os.path.isfile(metadata_filename):
                with open(metadata_filename, 'r') as f:
                    metadata = json.load(f)

                creation_time = datetime.datetime.fromisoformat(metadata["creation_time"])
                if (now - creation_time).days >= days:
                    os.remove(os.path.join(directory, filename))
                    os.remove(metadata_filename)  # Delete the metadata file
                    print(f"Deleted old video file: {filename}")