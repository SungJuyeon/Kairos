from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, Response
import cv2
import numpy as np
import tensorflow as tf
from scipy.spatial.distance import cosine
from scipy.ndimage import zoom
import time
import os
import json

from emotion_video import save_frames_to_video


# 감정 결과 저장 및 조회 함수
def get_emotion_file(date=None):
    base_dir = os.path.abspath("../Backend_Logic/emotions")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if date is None:
        date = datetime.today().strftime('%Y%m%d')
    return os.path.join(base_dir, f"{date}.json")


def initialize_emotion_data():
    return {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}


# 감정 결과 저장 함수
def save_emotion_result(emotion):
    file_path = get_emotion_file()

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


def get_emotion_ranking(date):
    file_path = get_emotion_file(date)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            emotion_data = json.load(file)
        sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
        return sorted_emotions
    else:
        return []


def get_most_frequent_emotion(date=None):
    file_path = get_emotion_file(date)
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


def manage_daily_files():
    today_file = get_emotion_file()
    yesterday_file = get_emotion_file(datetime.today() - timedelta(days=1))

    if not os.path.exists(today_file):
        with open(today_file, 'w') as file:
            json.dump(initialize_emotion_data(), file)

    if os.path.exists(yesterday_file):
        os.remove(yesterday_file)


# Flask 애플리케이션
app = Flask(__name__)

emotion_counts = defaultdict(int)
current_date = datetime.now().strftime('%Y-%m-%d')

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


# 감정 발생 횟수를 기록하는 함수
def record_emotion(emotion):
    global current_date
    today = datetime.now().strftime('%Y-%m-%d')
    if today != current_date:
        # 새로운 날이 되면 감정 데이터 초기화
        emotion_counts.clear()
        current_date = today
    emotion_counts[(today, emotion)] += 1
    print(f"Emotion recorded: {emotion}, Count: {emotion_counts[(today, emotion)]}")

    # Save emotion result to file
    save_emotion_result(emotion)

def compare_faces(face1, face2):
    return cosine(face1.flatten(), face2.flatten())


def recognize_face(detected_face):
    if registered_face is None:
        return None
    distance = compare_faces(detected_face, registered_face)
    if distance < 0.4:
        return registered_name
    return None


def detect_face(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48),
                                                   flags=cv2.CASCADE_SCALE_IMAGE)
    coord = []
    for (x, y, w, h) in detected_faces:
        if w > 100:
            coord.append([x, y, w, h])
    return gray, detected_faces, coord


def extract_face_features(gray, detected_faces, coord, offset_coefficients=(0.075, 0.05)):
    new_face = []
    for det in detected_faces:
        x, y, w, h = det
        horizontal_offset = int(np.floor(offset_coefficients[0] * w))
        vertical_offset = int(np.floor(offset_coefficients[1] * h))
        extracted_face = gray[y + vertical_offset:y + h, x + horizontal_offset:x - horizontal_offset + w]
        new_extracted_face = zoom(extracted_face, (48 / extracted_face.shape[0], 48 / extracted_face.shape[1]))
        new_extracted_face = new_extracted_face.astype(np.float32) / new_extracted_face.max()
        new_face.append(new_extracted_face)
    return new_face


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

        gray, detected_faces, coord = detect_face(frame)

        if len(detected_faces) > 0 and len(coord) > 0:
            x, y, w, h = coord[0]
            face_zoom = extract_face_features(gray, detected_faces, coord)
            face_zoom = np.reshape(face_zoom[0].flatten(), (1, 48, 48, 1))

            # 등록된 얼굴과 비교
            recognized_name = recognize_face(face_zoom[0])

            if recognized_name:
                # 얼굴이 등록된 경우에만 감정 인식 수행
                pred = model.predict(face_zoom)
                pred_result = np.argmax(pred)

                current_emotion = emotion_dict[pred_result]
                current_emotion_probability = round(pred[0][pred_result] * 100, 2)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.putText(frame, f"Recognized: {recognized_name}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)

                # 감정 확률이 높은 경우 비디오 저장 시작
                if current_emotion_probability > 90.0 and not saving_video:
                    video_filename = f"{recognized_name}_{int(time.time())}.avi"
                    saving_video = True
                    start_time = time.time()

                # 감정 발생 횟수를 기록
                if current_emotion_probability > 0:
                    record_emotion(current_emotion)
            else:
                # 얼굴이 등록되지 않은 경우, 감정 인식 및 비디오 저장 하지 않음
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


def load_registered_face(image_path):
    global registered_face, registered_name

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"The file at {image_path} does not exist.")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image from path: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48), flags=cv2.CASCADE_SCALE_IMAGE)

    # Debugging: Draw rectangles around detected faces
    for (x, y, w, h) in detected_faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Save the debug image
    cv2.imwrite("debug_detected_faces.jpg", image)

    if len(detected_faces) > 0:
        x, y, w, h = detected_faces[0]
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (48, 48))
        registered_face = face
        registered_name = "juyeon"  # Image filename or unique name can be used
    else:
        raise ValueError("No face detected in the image.")


@app.route('/register_face', methods=['POST'])
def register_face_route():
    global registered_face, registered_name

    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'No file or name provided'}), 400

    file = request.files['file']
    name = request.form['name']

    if file and name:
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48),
                                                       flags=cv2.CASCADE_SCALE_IMAGE)

        if len(detected_faces) > 0:
            x, y, w, h = detected_faces[0]
            face = gray[y:y + h, x:x + w]
            face = cv2.resize(face, (48, 48))
            registered_face = face
            registered_name = name
            return jsonify({'status': 'Face registered successfully'}), 200
        else:
            return jsonify({'error': 'No face detected in the image'}), 400
    else:
        return jsonify({'error': 'Invalid file or name'}), 400


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
    # 애플리케이션 시작 시 얼굴 데이터 로드
    try:
        load_registered_face("C:/Users/MJ/Downloads/Kairos/Backend_Logic/registered_faces/juyeonn.png")
        print("Registered face loaded successfully.")
    except Exception as e:
        print(f"Error loading registered face: {e}")
    app.run(debug=True)
