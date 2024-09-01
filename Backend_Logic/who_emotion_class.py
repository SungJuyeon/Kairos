import cv2
import numpy as np
from deepface import DeepFace
import os
import re
from datetime import datetime, timedelta
import time

from emotion_record import record_emotion, manage_daily_files, get_most_frequent_emotion


class FaceRecognition:
    def __init__(self, registered_faces_folder, model_prototxt, model_weights):
        self.registered_faces = self.load_registered_faces(registered_faces_folder)
        self.model = cv2.dnn.readNetFromCaffe(model_prototxt, model_weights)
        self.last_detected_nickname = "unknown"
        self.last_detected_distance = None
        self.last_face_position = None
        self.last_detected_emotion = "unknown"
        self.last_detected_emotion_scores = {}
        self.frames_to_save = []
        self.saving_video = False
        self.video_filename = ""
        self.cleanup_interval = 86400  # 24 hours in seconds

    def load_registered_faces(self, folder_path):
        registered_faces = []
        for filename in os.listdir(folder_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                registered_faces.append(os.path.join(folder_path, filename))
        return registered_faces

    def get_nickname_from_filename(self, filename):
        base_name = os.path.splitext(os.path.basename(filename))[0]
        nickname = re.sub(r'\s*\(.*?\)', '', base_name)
        return nickname.strip()

    def detect_faces(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.model.setInput(blob)
        detections = self.model.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))

        return faces

    def recognize_emotion(self, face_image):
        try:
            emotion_result = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False)
            print(emotion_result)
            if emotion_result:
                return emotion_result[0]['dominant_emotion'], emotion_result[0]['emotion']
            else:
                return "unknown", {}
        except Exception as e:
            print("Error in emotion recognition:", e)
            return "unknown", {}

    def recognize_faces(self, frame, faces):
        if len(faces) == 0:
            self.last_detected_nickname = "unknown"
            self.last_detected_distance = None
            self.last_detected_emotion = "unknown"
            self.last_detected_emotion_scores = {}
            return

        for (x, y, w, h) in faces:
            face_image = frame[y:y + h, x:x + w]

            try:
                result = DeepFace.find(face_image, db_path='faces', model_name='VGG-Face', enforce_detection=False)
                threshold = 0.4
                filtered_results = [res for res in result if res['distance'].values[0] < threshold]

                if len(filtered_results) > 0:
                    matched_face_path = filtered_results[0]['identity'].values[0]
                    self.last_detected_distance = filtered_results[0]['distance'].values[0]
                    self.last_detected_nickname = self.get_nickname_from_filename(matched_face_path)
                    self.last_face_position = (x, y, w, h)
                else:
                    self.last_detected_nickname = "unknown"
                    self.last_detected_distance = None

                self.last_detected_emotion, self.last_detected_emotion_scores = self.recognize_emotion(face_image)

                # 감정 점수가 90을 넘는 경우 비디오 저장 시작
                if self.last_detected_emotion_scores:
                    max_emotion_score = max(self.last_detected_emotion_scores.values())
                    if max_emotion_score > 90:
                        if not self.saving_video:
                            self.start_saving_video()
                    elif self.saving_video:
                        self.stop_saving_video()

                # 감정 기록
                record_emotion(self.last_detected_emotion)

            except Exception as e:
                print("Error in face recognition:", e)
                self.last_detected_emotion = "unknown"
                self.last_detected_emotion_scores = {}

    def draw_faces(self, frame, faces):
        if self.last_face_position is not None:
            (x, y, w, h) = self.last_face_position
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if self.last_detected_distance is not None:
                cv2.putText(frame, f"Detected: {self.last_detected_nickname} ({self.last_detected_distance:.2f})",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Detected: {self.last_detected_nickname}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if self.last_detected_emotion_scores:
                sorted_emotions = sorted(self.last_detected_emotion_scores.items(), key=lambda item: item[1], reverse=True)
                top_emotion, top_score = sorted_emotions[0]
                cv2.putText(frame, f"{top_emotion}: {top_score:.2f}%", (x + w + 10, y + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

                for i, (emotion, score) in enumerate(sorted_emotions[1:], start=1):
                    cv2.putText(frame, f"{emotion}: {score:.2f}%", (x + w + 10, y + 25 + i * 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        for (x, y, w, h) in faces:
            if (x, y, w, h) != self.last_face_position:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

    def start_saving_video(self):
        self.frames_to_save = []
        self.saving_video = True
        self.video_filename = self.generate_video_filename()
        self.start_time = time.time()
        print(f"Started saving video to {self.video_filename}")

    def stop_saving_video(self):
        self.saving_video = False
        self.save_frames_to_video(self.video_filename, self.frames_to_save)
        print(f"Stopped saving video and saved to {self.video_filename}")

    def generate_video_filename(self):
        base_dir = "videos"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        today = datetime.today().strftime('%Y%m%d')
        if self.last_detected_nickname == "unknown":
            name_part = "unknown"
        else:
            name_part = self.last_detected_nickname

        existing_files = [f for f in os.listdir(base_dir) if f.startswith(today) and f.endswith('.avi')]
        existing_numbers = []
        for filename in existing_files:
            match = re.match(rf"{today}_{name_part}_(\d+).avi", filename)
            if match:
                number = int(match.group(1))
                existing_numbers.append(number)

        next_number = 1 if not existing_numbers else max(existing_numbers) + 1
        return os.path.join(base_dir, f"{today}_{name_part}_{next_number}.avi")

    def save_frames_to_video(self, filename, frames, frame_rate=5):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        height, width, layers = frames[0].shape
        out = cv2.VideoWriter(filename, fourcc, frame_rate, (width, height))

        for frame in frames:
            out.write(frame)

        out.release()

    def cleanup_old_videos(self):
        base_dir = "videos"
        today = datetime.today()
        cutoff_time = today - timedelta(days=2)

        for filename in os.listdir(base_dir):
            if filename.endswith('.avi'):
                filepath = os.path.join(base_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if file_time < cutoff_time:
                    os.remove(filepath)
                    print(f"Removed old video: {filepath}")

    def process_video_stream(self):
        cap = cv2.VideoCapture(0)
        frame_counter = 0

        manage_daily_files()  # 초기화된 감정 파일 관리

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            faces = self.detect_faces(frame)

            if frame_counter % 7 == 0:
                self.recognize_faces(frame, faces)

            if self.saving_video:
                self.frames_to_save.append(frame)

            self.draw_faces(frame, faces)
            cv2.imshow('Video Stream', frame)

            frame_counter += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        # 하루가 끝난 후 최다 감정 저장 및 초기화
        most_frequent_emotion = get_most_frequent_emotion()
        if most_frequent_emotion[1] > 0:
            print(f"Most frequent emotion today: {most_frequent_emotion[0]} with {most_frequent_emotion[1]} occurrences.")
            with open('most_frequent_emotion.json', 'w') as file:
                import json
                json.dump({most_frequent_emotion[0]: most_frequent_emotion[1]}, file)

        manage_daily_files()  # 하루가 끝난 후 파일 초기화

        self.cleanup_old_videos()  # 비디오 파일 정리 호출

# 사용 예시
if __name__ == "__main__":
    face_recognition = FaceRecognition(
        registered_faces_folder='faces',
        model_prototxt='models/deploy.prototxt',
        model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
    )

    face_recognition.process_video_stream()
