import cv2
import numpy as np
import tensorflow as tf
from scipy.ndimage import zoom
from flask import Flask, render_template, Response, jsonify
import time
import os
from datetime import datetime
import asyncio


app = Flask(__name__)

# 모델 로드 (Keras .h5 형식)
model = tf.keras.models.load_model('emotion_detection_model.h5')

# 감정 레이블 매핑
emotion_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

# 현재 감정 상태를 저장할 변수
current_emotion = 'None'
current_emotion_probability = 0.0

# 영상 저장을 위한 변수
saving_video = False
video_writer = None
video_filename = ""
frame_rate = 5  # 저장할 영상 프레임 설정
video_duration = 10  # 10초간 영상 저장

# 비디오 저장 경로 및 파일명 생성 함수
def generate_video_filename():
    base_dir = "videos"  # 비디오 파일 저장 폴더
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)  # 폴더가 없으면 생성

    today = datetime.today().strftime('%Y%m%d')  # 오늘 날짜
    return os.path.join(base_dir, f"{today}.avi")  # 비디오 파일 경로, 이름 반환

# 얼굴 감지 함수
def detect_face(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # Haarcascade 파일 로드
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 프레임을 그레이스케일로 변환
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48), flags=cv2.CASCADE_SCALE_IMAGE)  # 얼굴 감지
    coord = []  # 얼굴 좌표 저장
    for (x, y, w, h) in detected_faces:  # 감지된 얼굴들을 순회
        if w > 100:  # 특정 크기 이상의 얼굴만 선택
            coord.append([x, y, w, h])  # 좌표 리스트에 추가
    return gray, detected_faces, coord  # 그레이스케일 이미지, 감지된 얼굴, 좌표 반환

# 얼굴 특징 추출 함수
def extract_face_features(gray, detected_faces, coord, offset_coefficients=(0.075, 0.05)):
    new_face = []  # 새로운 얼굴 리스트
    for det in detected_faces:  # 감지된 얼굴들을 순회
        x, y, w, h = det  # 얼굴 좌표
        horizontal_offset = int(np.floor(offset_coefficients[0] * w))  # 가로 오프셋 계산
        vertical_offset = int(np.floor(offset_coefficients[1] * h))  # 세로 오프셋 계산
        extracted_face = gray[y+vertical_offset:y+h, x+horizontal_offset:x-horizontal_offset+w]  # 얼굴 특징 추출
        new_extracted_face = zoom(extracted_face, (48/extracted_face.shape[0], 48/extracted_face.shape[1]))  # 얼굴 이미지를 48x48로 리사이즈
        new_extracted_face = new_extracted_face.astype(np.float32) / new_extracted_face.max()  # 이미지 정규화
        new_face.append(new_extracted_face)  # 새로운 얼굴 리스트에 추가
    return new_face  # 추출된 얼굴 특징 반환

# 비디오 파일이 존재하면 이어서 작성할 수 있도록 VideoWriter 객체를 생성하는 함수
def create_video_writer(filename):
    global video_capture, frame_rate
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, frame_rate, (int(video_capture.get(3)), int(video_capture.get(4))))
    return video_writer

# 비디오 프레임 생성기
def generate_frames():
    global current_emotion, current_emotion_probability, saving_video, video_writer, video_filename, video_capture
    video_capture = cv2.VideoCapture(0)  # 웹캠 비디오 캡처 객체 생성

    frame_rate = 20.0  # 프레임 레이트 설정
    frames_to_save = int(frame_rate * video_duration)  # 10초간 저장할 프레임 수
    start_time = None  # 저장 시작 시간을 기록하기 위한 변수

    while True:
        ret, frame = video_capture.read()  # 프레임 읽기
        if not ret:
            break

        face_index = 0  # 첫 번째 얼굴 인덱스
        gray, detected_faces, coord = detect_face(frame)  # 얼굴 감지 및 좌표 획득

        if len(detected_faces) > 0 and len(coord) > 0:  # 얼굴이 감지되었고 coord 리스트가 비어있지 않을 때
            x, y, w, h = coord[face_index]  # 얼굴 좌표 가져오기

            face_zoom = extract_face_features(gray, detected_faces, coord)  # 얼굴 특징 추출
            face_zoom = np.reshape(face_zoom[0].flatten(), (1, 48, 48, 1))  # 모델 입력 형태로 변환

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)  # 얼굴에 사각형 그리기

            pred = model.predict(face_zoom)  # 감정 예측
            pred_result = np.argmax(pred)  # 가장 높은 확률의 감정 인덱스 가져오기

            current_emotion = emotion_dict[pred_result]  # 현재 감정 설정
            current_emotion_probability = round(pred[0][pred_result] * 100, 2)  # 감정 확률 설정

            cv2.putText(frame, f"{current_emotion}: {current_emotion_probability}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # 감정과 확률 표시

            if current_emotion_probability > 90.0 and not saving_video:  # 감정 확률이 90%를 넘고, 아직 저장 중이 아닐 때
                video_filename = generate_video_filename()  # 비디오 파일명 생성

                # 기존 파일이 존재하면 이어서 작성하기 위해 열기
                if os.path.exists(video_filename):
                    video_writer = create_video_writer(video_filename)
                else:
                    video_writer = create_video_writer(video_filename)

                saving_video = True  # 저장 시작
                start_time = time.time()  # 저장 시작 시간 기록

        # 감정과 상관없이 저장 중일 때 프레임을 저장
        if saving_video:
            video_writer.write(frame)  # 현재 프레임 저장

            # 10초가 경과하면 저장 종료
            if time.time() - start_time >= video_duration:
                saving_video = False  # 저장 종료
                video_writer.release()  # 비디오 작성 객체 해제
                start_time = None  # 시작 시간 초기화

        # 얼굴이 감지되지 않았을 경우에도 프레임을 계속 스트리밍
        ret, buffer = cv2.imencode('.jpg', frame)  # 프레임을 JPEG 형식으로 인코딩
        frame = buffer.tobytes()  # 프레임을 바이트 형식으로 변환
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 프레임을 HTTP 응답으로 전달

        cv2.waitKey(10)  # 10ms 0.01초 간격 대기

    video_capture.release()  # 비디오 캡처 객체 해제
    if video_writer is not None:
        video_writer.release()  # 비디오 작성 객체 해제

# 웹 페이지를 위한 라우트 설정
@app.route('/')
def index():
    return render_template('emotion.html')  # emotion.html 렌더링

# 비디오 피드를 위한 라우트 설정
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # 비디오 피드 응답

# 현재 감정을 반환하는 라우트 설정
@app.route('/current_emotion')
def get_current_emotion():
    return jsonify(emotion=current_emotion, probability=current_emotion_probability)  # JSON 형식으로 감정 반환

# 서버 시작
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
