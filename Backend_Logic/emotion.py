import os
import cv2
import numpy as np
import tensorflow as tf
import time
from datetime import datetime
from flask import Flask, jsonify, request, render_template, Response

from compare_faces import compare_faces, get_similarity_percentage
from emotion_video import save_frames_to_video
from face_register import detect_face, extract_face_features
from emotion_record import save_emotion_result, manage_daily_files, get_most_frequent_emotion, record_emotion

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

registered_face = None
registered_name = None

# 실시간 스트림에서 얼굴 비교 및 감정 분석 수행
def generate_frames():
    global current_emotion, current_emotion_probability, saving_video, video_filename
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    frames_to_save = []
    start_time = None

    # Load the registered face (db.png)
    db_image_path = os.path.abspath("db.png")
    if not os.path.exists(db_image_path):
        raise FileNotFoundError("The registered face image db.png does not exist.")

    registered_face = cv2.imread(db_image_path, cv2.IMREAD_GRAYSCALE)
    if registered_face is None:
        raise ValueError("Failed to load registered face image.")

    # 등록된 얼굴을 48x48로 리사이즈하여 비교 준비
    registered_face = cv2.resize(registered_face, (48, 48))

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray, detected_faces, coord = detect_face(frame)

        if len(detected_faces) > 0 and len(coord) > 0:
            x, y, w, h = coord[0]
            face_zoom = extract_face_features(gray, detected_faces, coord)
            face_zoom_resized = np.reshape(face_zoom[0], (48, 48))

            # 얼굴 비교
            similarity_percentage = get_similarity_percentage(face_zoom_resized, registered_face) * 100
            print(f"Similarity percentage: {similarity_percentage:.2f}%")

            if similarity_percentage > 90:  # 유사도 기준치를 90% 이상으로 설정
                pred = model.predict(np.expand_dims(face_zoom_resized, axis=0))
                pred_result = np.argmax(pred)

                current_emotion = emotion_dict[pred_result]
                current_emotion_probability = round(pred[0][pred_result] * 100, 2)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.putText(frame, f"Recognized: {registered_name}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)

                # 얼굴 일치 비율을 비디오에 표시
                cv2.putText(frame, f"Similarity: {similarity_percentage:.2f}%", (x, y + h + 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 0), 2)

                # 감정 확률이 높은 경우 비디오 저장 시작
                if current_emotion_probability > 90.0 and not saving_video:
                    video_filename = f"{registered_name}_{int(time.time())}.avi"
                    saving_video = True
                    start_time = time.time()

                # 감정 발생 횟수를 기록
                if current_emotion_probability > 0:
                    record_emotion(current_emotion)
            else:
                # 얼굴이 일치하지 않는 경우
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Unrecognized face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if saving_video:
            frames_to_save.append(frame)

            if time.time() - start_time >= video_duration:
                save_frames_to_video(video_filename, frames_to_save)
                saving_video = False
                frames_to_save = []
                start_time = None

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cv2.waitKey(1)


# Routes
@app.route('/emotion')
def index():
    return render_template('emotion.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/most_frequent_emotion')
def most_frequent_emotion():
    most_frequent, count = get_most_frequent_emotion()
    return jsonify({"emotion": most_frequent, "count": count})

@app.route('/current_emotion')
def get_current_emotion():
    return jsonify(emotion=current_emotion, probability=current_emotion_probability)

# 하루가 끝날 때 감정 데이터 관리
manage_daily_files()

if __name__ == '__main__':
    # 애플리케이션 시작 시 등록된 얼굴 데이터 로드
    try:
        registered_face_path = "C:/Users/MJ/Downloads/Kairos/Backend_Logic/registered_faces/juyeonn.png"
        registered_face = cv2.imread(registered_face_path, cv2.IMREAD_GRAYSCALE)

        if registered_face is None:
            raise ValueError("Failed to load the registered face image.")

        # 등록된 얼굴을 48x48로 리사이즈하여 비교 준비
        registered_face = cv2.resize(registered_face, (48, 48))
        print("Registered face loaded and resized successfully.")

    except Exception as e:
        print(f"Error loading registered face: {e}")

    app.run(debug=True)
