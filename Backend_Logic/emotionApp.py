from flask import Flask, jsonify, request, render_template, Response
import cv2
import numpy as np
import tensorflow as tf
import time
import os

from face_register import detect_face
from face_recog import FaceRecog  # 얼굴 인식을 위한 클래스
from emotion_record import save_emotion_result, get_most_frequent_emotion, manage_daily_files, record_emotion
from emotion_video import save_frames_to_video, generate_video_filename, delete_old_videos

# Flask 애플리케이션
app = Flask(__name__)

emotion_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
model = tf.keras.models.load_model('emotion_detection_model.h5')

current_emotion = 'None'
current_emotion_probability = 0.0
saving_video = False
video_filename = ""
frame_rate = 5
video_duration = 10

# FaceRecog 인스턴스 생성
face_recog = FaceRecog()

def generate_frames():
    global current_emotion, current_emotion_probability, saving_video, video_filename
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    frames_to_save = []
    start_time = None

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # 감정 분석 및 얼굴 인식
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 얼굴 인식 결과를 프레임에 반영
        frame, face_names = face_recog.get_frame(frame)  # 두 값 반환 처리

        gray, detected_faces, coord = detect_face(frame)

        if len(detected_faces) > 0 and len(coord) > 0:
            x, y, w, h = coord[0]
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (48, 48))
            face_resized = np.reshape(face_resized, (1, 48, 48, 1)) / 255.0

            # 감정 예측
            pred = model.predict(face_resized)
            pred_probabilities = pred[0]
            pred_result = np.argmax(pred_probabilities)

            current_emotion = emotion_dict[pred_result]
            current_emotion_probability = round(pred_probabilities[pred_result] * 100, 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if current_emotion_probability > 0:
                record_emotion(current_emotion)

            if current_emotion_probability > 90.0 and not saving_video:
                video_filename = f"{int(time.time())}.avi"
                saving_video = True
                start_time = time.time()

        if saving_video:
            frames_to_save.append(frame)

            if time.time() - start_time >= video_duration:
                save_frames_to_video(video_filename, frames_to_save)
                saving_video = False
                frames_to_save = []
                start_time = None

        # 프레임을 MJPEG 스트림으로 변환
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cv2.waitKey(1)

    video_capture.release()
    cv2.destroyAllWindows()


@app.route('/emotion')
def index():
    return render_template('emotion.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/most_frequent_emotion')
def most_frequent_emotion():
    try:
        manage_daily_files()
        emotion, count = get_most_frequent_emotion()
        return jsonify(emotion=emotion, count=count)
    except Exception as e:
        print(f"Error in /most_frequent_emotion: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving the most frequent emotion."}), 500

@app.route('/current_emotion')
def get_current_emotion():
    return jsonify(emotion=current_emotion, probability=current_emotion_probability)

if __name__ == '__main__':
    delete_old_videos('videos', days=2)
    app.run(debug=True)
