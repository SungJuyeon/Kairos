import cv2
import numpy as np
from deepface import DeepFace
import asyncio
from concurrent.futures import ThreadPoolExecutor


class FaceRecognition:
    def __init__(self, registered_faces_folder, model_prototxt, model_weights):
        self.model = cv2.dnn.readNetFromCaffe(model_prototxt, model_weights)
        self.last_detected_nicknames = []
        self.last_detected_distances = []
        self.last_face_positions = []
        self.last_detected_emotions = []
        self.last_detected_emotion_scores = []
        self.executor = ThreadPoolExecutor(max_workers=4)

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
            if emotion_result:
                return emotion_result[0]['dominant_emotion'], emotion_result[0]['emotion']
            else:
                return "unknown", {}
        except Exception as e:
            print("Error in emotion recognition:", e)
            return "unknown", {}

    def recognize_faces(self, frame, faces):
        self.last_detected_nicknames.clear()
        self.last_detected_distances.clear()
        self.last_face_positions.clear()
        self.last_detected_emotions.clear()
        self.last_detected_emotion_scores.clear()

        for (x, y, w, h) in faces:
            face_image = frame[y:y + h, x:x + w]

            try:
                result = DeepFace.find(face_image, db_path='../faces', model_name='VGG-Face', enforce_detection=False)
                threshold = 0.4
                filtered_results = [res for res in result if res['distance'].values[0] < threshold]

                if len(filtered_results) > 0:
                    matched_face_path = filtered_results[0]['identity'].values[0]
                    self.last_detected_distances.append(filtered_results[0]['distance'].values[0])
                    self.last_detected_nicknames.append(self.get_nickname_from_filename(matched_face_path))
                    self.last_face_positions.append((x, y, w, h))
                else:
                    self.last_detected_nicknames.append("unknown")
                    self.last_detected_distances.append(None)
                    self.last_face_positions.append((x, y, w, h))

                emotion, scores = self.recognize_emotion(face_image)
                self.last_detected_emotions.append(emotion)
                self.last_detected_emotion_scores.append(scores)

            except Exception as e:
                print("Error in face recognition:", e)
                self.last_detected_emotions.append("unknown")
                self.last_detected_emotion_scores.append({})

    def draw_faces(self, frame, faces):
        for idx, (x, y, w, h) in enumerate(faces):
            # 모든 얼굴에 대해 노란색 네모를 그립니다.
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 노란색

            # 인식된 얼굴에 대해서는 초록색 네모를 추가로 그립니다.
            if idx < len(self.last_detected_nicknames) and self.last_detected_nicknames[idx] != "unknown":
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색
                nickname = self.last_detected_nicknames[idx]
                distance = self.last_detected_distances[idx]
                emotion = self.last_detected_emotions[idx]
                scores = self.last_detected_emotion_scores[idx]

                if distance is not None:
                    cv2.putText(frame, f"Detected: {nickname} ({distance:.2f})",
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, f"Detected: {nickname}",
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                if scores:
                    sorted_emotions = sorted(scores.items(), key=lambda item: item[1], reverse=True)
                    top_emotion, top_score = sorted_emotions[0]
                    cv2.putText(frame, f"{top_emotion}: {top_score:.2f}%", (x + w + 10, y + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

                    for i, (emotion, score) in enumerate(sorted_emotions[1:], start=1):
                        cv2.putText(frame, f"{emotion}: {score:.2f}%", (x + w + 10, y + 25 + i * 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                # 인식 실패 시 텍스트 표시
                cv2.putText(frame, "No recognition data", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    def process_video_stream(self):
        cap = cv2.VideoCapture(0)
        frame_counter = 0
        self.loop = asyncio.get_event_loop()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            faces = self.detect_faces(frame)

            if frame_counter == 0:
                self.recognize_faces(frame, faces)

            self.draw_faces(frame, faces)
            cv2.imshow('Video Stream', frame)

            frame_counter += 1
            frame_counter %= 7

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# 사용 예시
if __name__ == "__main__":
    face_recognition = FaceRecognition(
        registered_faces_folder='faces',
        model_prototxt='models/deploy.prototxt',
        model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
    )

    face_recognition.process_video_stream()
