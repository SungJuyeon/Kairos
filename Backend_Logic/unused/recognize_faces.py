import cv2
import numpy as np
import pandas as pd
from deepface import DeepFace
import os
import re

class FaceEmotionRecognizer:
    def __init__(self, model_path, embeddings_file):
        self.model = cv2.dnn.readNetFromCaffe(model_path + "deploy.prototxt", model_path + "res10_300x300_ssd_iter_140000.caffemodel")
        self.embeddings = self.load_face_embeddings(embeddings_file)

    def load_face_embeddings(self, input_file):
        df = pd.read_csv(input_file)
        return {row['identity']: np.array(eval(row['embedding'])) for _, row in df.iterrows()}

    @staticmethod
    def get_nickname_from_filename(filename):
        return re.sub(r'\s*\(.*?\)', '', os.path.splitext(os.path.basename(filename))[0]).strip()

    def detect_faces(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.model.setInput(blob)
        detections = self.model.forward()

        faces = []
        for i in range(detections.shape[2]):
            if detections[0, 0, i, 2] > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))
        return faces

    def recognize_face_and_emotion(self, face_image, threshold=0.4):
        try:
            if face_image.size == 0:
                return {}, None

            face_embedding = DeepFace.represent(face_image, model_name='VGG-Face', enforce_detection=False)
            if not face_embedding:
                return {}, None

            face_embedding = face_embedding[0]["embedding"]
            distances = {identity: np.linalg.norm(face_embedding - embedding) for identity, embedding in self.embeddings.items()}
            filtered_results = {identity: dist for identity, dist in distances.items() if dist < threshold}

            # 감정 인식
            emotion_analysis = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False)
            emotion_scores = emotion_analysis[0]['emotion'] if emotion_analysis else {}

            return filtered_results, emotion_scores
        except Exception as e:
            print("Error in face recognition or emotion analysis:", e)
            return {}, None

    def process_frame(self, frame):
        faces = self.detect_faces(frame)
        results = []

        for (x, y, w, h) in faces:
            face_image = frame[y:y + h, x:x + w]
            matched_faces, emotion_scores = self.recognize_face_and_emotion(face_image)

            if matched_faces:
                matched_identity = list(matched_faces.keys())[0]
                distance = matched_faces[matched_identity]
                nickname = self.get_nickname_from_filename(matched_identity)
                dominant_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else None
                dominant_score = emotion_scores[dominant_emotion] if dominant_emotion else None
                results.append({
                    'nickname': nickname,
                    'distance': distance,
                    'dominant_emotion': dominant_emotion,
                    'dominant_score': dominant_score,
                    'box': (x, y, w, h)
                })
            else:
                results.append({
                    'nickname': 'unknown',
                    'dominant_emotion': None,
                    'dominant_score': None,
                    'box': (x, y, w, h)
                })

        return results

    def display_results(self, frame, results):
        for result in results:
            (x, y, w, h) = result['box']
            if result['nickname'] != 'unknown':
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Detected: {result['nickname']} ({result['distance']:.2f})", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                if result['dominant_emotion'] and result['dominant_score'] is not None:
                    cv2.putText(frame, f"{result['dominant_emotion']}: {result['dominant_score']:.2f}%", (x + w + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)


# 사용 예
if __name__ == "__main__":
    recognizer = FaceEmotionRecognizer(model_path="../models/", embeddings_file='faces/face_embeddings.csv')

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = recognizer.process_frame(frame)
        recognizer.display_results(frame, results)

        cv2.imshow('Video Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
