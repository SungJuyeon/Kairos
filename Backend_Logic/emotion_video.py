import cv2

def save_frames_to_video(filename, frames):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    height, width, _ = frames[0].shape
    video_writer = cv2.VideoWriter(filename, fourcc, 30, (width, height))

    for frame in frames:
        video_writer.write(frame)

    video_writer.release()
