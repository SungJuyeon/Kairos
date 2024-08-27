import os
import cv2
import numpy as np
import tensorflow as tf
import time
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
def initialize_registered_face():
    global registered_face, registered_name

    try:
        registered_face_path = "C:/Users/MJ/Downloads/Kairos/Backend_Logic/registered_faces/juyeonn.png"
        db_image_path = "C:/Users/MJ/Downloads/Kairos/Backend_Logic/registered_faces/db.png"

        # Load and process registered face image
        if not os.path.exists(registered_face_path):
            raise FileNotFoundError(f"The registered face image {registered_face_path} does not exist.")

        registered_face = cv2.imread(registered_face_path)
        if registered_face is None:
            raise ValueError("Failed to load the registered face image.")

        registered_face = cv2.resize(registered_face, (48, 48))
        print("Registered face loaded and resized successfully.")

        # Save the processed registered face as db.png
        cv2.imwrite(db_image_path, registered_face)
        print(f"Registered face image saved as db.png at {db_image_path}")

        # Load and process db.png
        if not os.path.exists(db_image_path):
            raise FileNotFoundError(f"The db image {db_image_path} does not exist.")

        db_image = cv2.imread(db_image_path)
        if db_image is None:
            raise ValueError("Failed to load the db image.")

        gray_db_image = cv2.cvtColor(db_image, cv2.COLOR_BGR2GRAY)
        gray_db_image, faces_db_image, coord_db_image = detect_face(db_image)
        print(f"Detected faces in db image: {coord_db_image}")

        # Resizing and preparing db image face for comparison (if needed)
        if len(faces_db_image) > 0:
            face_zoom_db = extract_face_features(gray_db_image, faces_db_image, coord_db_image)
            if face_zoom_db is not None and len(face_zoom_db) > 0:
                face_zoom_db = face_zoom_db[0]  # Use the first face
                face_zoom_db_resized = cv2.resize(face_zoom_db, (48, 48))
                face_zoom_db_resized = cv2.cvtColor(face_zoom_db_resized, cv2.COLOR_BGR2RGB)
                print(f"db.png face_zoom shape: {face_zoom_db_resized.shape}")
            else:
                print("No faces detected in db.png after feature extraction.")
        else:
            print("No faces detected in db.png.")

    except Exception as e:
        print(f"Error initializing registered face: {e}")
        raise


def generate_frames():
    global current_emotion, current_emotion_probability, saving_video, video_filename

    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    frames_to_save = []
    start_time = None

    while True:
        try:
            ret, frame = video_capture.read()
            if not ret:
                break

            gray, detected_faces, coord = detect_face(frame)
            print(f"Detected faces in frame: {coord}")

            if len(detected_faces) > 0 and len(coord) > 0:
                x, y, w, h = coord[0]
                face_zoom = extract_face_features(gray, detected_faces, coord)

                if face_zoom is not None and len(face_zoom) > 0:
                    face_zoom = face_zoom[0]  # 첫 번째 얼굴만 사용
                    print(f"face_zoom shape: {face_zoom.shape}")

                    if len(face_zoom.shape) == 2:  # 그레이스케일인 경우
                        face_zoom_resized = cv2.cvtColor(face_zoom, cv2.COLOR_GRAY2RGB)
                    else:
                        face_zoom_resized = face_zoom

                    face_zoom_resized = cv2.resize(face_zoom_resized, (48, 48))
                    face_zoom_resized = cv2.cvtColor(face_zoom_resized, cv2.COLOR_BGR2RGB)  # 비교를 위해 RGB로 변환

                    # 얼굴 유사도 비교
                    similarity_percentage = get_similarity_percentage(face_zoom_resized, registered_face)
                    print(f"Similarity percentage: {similarity_percentage:.2f}%")

                    if similarity_percentage > 0:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, "Recognized", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, f"Similarity: {similarity_percentage:.2f}%", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                        # 감정 분석
                        pred = model.predict(np.expand_dims(face_zoom_resized, axis=0))
                        pred_result = np.argmax(pred)
                        current_emotion = emotion_dict[pred_result]
                        current_emotion_probability = round(pred[0][pred_result] * 100, 2)

                        cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y + h + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                        # 비디오 저장 조건
                        if current_emotion_probability > 90.0 and not saving_video:
                            video_filename = f"{registered_name}_{int(time.time())}.avi"
                            saving_video = True
                            start_time = time.time()

                        if current_emotion_probability > 0:
                            record_emotion(current_emotion)
                    else:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, "Recognized but Low Similarity", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(frame, f"Similarity: {similarity_percentage:.2f}%", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                else:
                    cv2.putText(frame, "Face detection failed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, "Unrecognized", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "No faces detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Unrecognized", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

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

        except Exception as e:
            print(f"Error in generate_frames: {e}")
            break

    video_capture.release()
    cv2.destroyAllWindows()

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
    try:
        # 애플리케이션 시작 시 등록된 얼굴 데이터 로드 및 검증
        initialize_registered_face()
        app.run(debug=True)
    except Exception as e:
        print(f"Application failed to start: {e}")
