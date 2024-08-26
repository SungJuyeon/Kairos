import base64
import os
import cv2
from io import BytesIO
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request, send_from_directory, render_template, Response
from werkzeug.utils import secure_filename
from scipy.spatial.distance import cosine
from scipy.ndimage import zoom
import time
from dotenv import load_dotenv
from faceDB import register_face_to_db, get_registered_faces_from_db
from emotion_ranking import get_emotion_ranking
from emotion_video import save_frames_to_video, generate_video_filename

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 애플리케이션
app = Flask(__name__)

# 감정 분류 모델 로드 (Keras .h5 형식)
model = tf.keras.models.load_model('emotion_detection_model.h5')

# 감정 레이블 매핑
emotion_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

# 현재 감정 상태를 저장할 변수
current_emotion = 'None'
current_emotion_probability = 0.0

# 영상 저장을 위한 변수
saving_video = False
video_filename = ""
frame_rate = 5  # 저장할 영상 프레임 설정
video_duration = 10  # 10초간 영상 저장

# 얼굴 등록 함수
def register_face(image, name):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48), flags=cv2.CASCADE_SCALE_IMAGE)

    if len(detected_faces) > 0:
        (x, y, w, h) = detected_faces[0]
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (48, 48))
        filename = f"{secure_filename(name)}.jpg"

        # 얼굴 이미지 저장
        if not os.path.exists("registered_faces"):
            os.makedirs("registered_faces")
        cv2.imwrite(os.path.join("registered_faces", filename), face)

        # 데이터베이스에 등록
        if register_face_to_db(face, name):
            return True
    return False

# 얼굴 비교 함수
def compare_faces(face1, face2):
    return cosine(face1.flatten(), face2.flatten())

# 얼굴 인식 함수
def recognize_face(detected_face):
    min_distance = float('inf')
    recognized_name = None
    faces_info = get_registered_faces_from_db()

    for face_info in faces_info:
        face_image = np.frombuffer(face_info['image_data'], np.uint8)
        face_image = cv2.imdecode(face_image, cv2.IMREAD_GRAYSCALE)
        distance = compare_faces(detected_face, face_image)
        if distance < min_distance and distance < 0.4:  # 코사인 유사도 기준
            min_distance = distance
            recognized_name = face_info['name']
    return recognized_name

# 얼굴 감지 함수
def detect_face(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48), flags=cv2.CASCADE_SCALE_IMAGE)
    coord = []
    for (x, y, w, h) in detected_faces:
        if w > 100:
            coord.append([x, y, w, h])
    return gray, detected_faces, coord

# 얼굴 특징 추출 함수
def extract_face_features(gray, detected_faces, coord, offset_coefficients=(0.075, 0.05)):
    new_face = []
    for det in detected_faces:
        x, y, w, h = det
        horizontal_offset = int(np.floor(offset_coefficients[0] * w))
        vertical_offset = int(np.floor(offset_coefficients[1] * h))
        extracted_face = gray[y+vertical_offset:y+h, x+horizontal_offset:x-horizontal_offset+w]
        new_extracted_face = zoom(extracted_face, (48/extracted_face.shape[0], 48/extracted_face.shape[1]))
        new_extracted_face = new_extracted_face.astype(np.float32) / new_extracted_face.max()
        new_face.append(new_extracted_face)
    return new_face

# 비디오 프레임 생성기
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

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            pred = model.predict(face_zoom)
            pred_result = np.argmax(pred)

            current_emotion = emotion_dict[pred_result]
            current_emotion_probability = round(pred[0][pred_result] * 100, 2)

            cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            recognized_name = recognize_face(face_zoom[0])

            if current_emotion_probability > 90.0 and not saving_video:
                video_filename = generate_video_filename()
                saving_video = True
                start_time = time.time()

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

# 웹 페이지를 위한 라우트 설정
@app.route('/emotion')
def index():
    return render_template('emotion.html')

# 비디오 피드를 위한 라우트 설정
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 현재 감정을 반환하는 라우트 설정
@app.route('/current_emotion')
def get_current_emotion():
    return jsonify(emotion=current_emotion, probability=current_emotion_probability)

# 감정 순위를 반환하는 라우트 설정
@app.route('/emotion_ranking')
def emotion_ranking():
    rankings = get_emotion_ranking()  # 감정 순위 가져오기
    return jsonify(rankings)  # JSON 형식으로 감정 순위 반환

# 얼굴 등록 라우트
@app.route('/register_face', methods=['POST'])
def register_face_route():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'No file or name provided'}), 400

    file = request.files['file']
    name = request.form['name']

    if file and name:
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        if register_face_to_db(image, name):
            return jsonify({'status': 'Face registered successfully'}), 200
        else:
            return jsonify({'error': 'Face registration failed'}), 400
    else:
        return jsonify({'error': 'Invalid file or name'}), 400

# 모든 등록된 얼굴 정보 조회 라우트
@app.route('/all_registered_faces', methods=['GET'])
def get_all_registered_faces_route():
    faces_info = get_registered_faces_from_db()

    face_list = []
    for face in faces_info:
        # 이미지 데이터를 Base64로 인코딩
        image_data_base64 = base64.b64encode(face['image_data']).decode('utf-8')
        face_list.append({
            'id': face['id'],
            'name': face['name'],
            'image_data': image_data_base64  # Base64 문자열로 변환된 이미지 데이터
        })

    return jsonify(face_list), 200

# 얼굴 이미지 파일 제공 라우트
@app.route('/face_images/<filename>', methods=['GET'])
def get_face_image(filename):
    return send_from_directory('registered_faces', filename)

# 서버 시작
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
