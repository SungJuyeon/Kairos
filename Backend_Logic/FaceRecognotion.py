import cv2
import numpy as np
from deepface import DeepFace
import asyncio
from concurrent.futures import ThreadPoolExecutor


class FaceRecognition:
    def __init__(self, registered_faces_folder, model_prototxt, model_weights):
        self.model = cv2.dnn.readNetFromCaffe(model_prototxt, model_weights)
        self.last_detected_nicknames = []  # 초기화 시 빈 리스트
        self.last_detected_distances = []  # 초기화 시 빈 리스트
        self.last_detected_rectangles = []  # 초기화 시 빈 리스트
        self.last_face_positions = []
        self.last_detected_emotions = []
        self.last_detected_emotion_scores = []
        self.faces = []  # 얼굴 정보를 저장할 멤버 변수
        self.executor = ThreadPoolExecutor(max_workers=4)

    def detect_faces(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.model.setInput(blob)
        detections = self.model.forward()

        self.faces.clear()  # 이전 얼굴 정보를 초기화

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.8:  # 신뢰도가 0.5 이상인 경우만 처리
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                self.faces.append((startX, startY, endX - startX, endY - startY))

        # 얼굴이 감지되지 않은 경우 None으로 설정
        if not self.faces:
            self.last_face_positions = None
        else:
            self.last_face_positions = self.faces

    async def recognize_faces(self, frame):
        if self.last_face_positions is None:
            self.last_detected_nicknames = ["unknown"]
            self.last_detected_distances = [None]
            self.last_detected_rectangles = []  # 빈 리스트로 초기화
            return

        self.last_detected_nicknames.clear()
        self.last_detected_distances.clear()
        self.last_detected_rectangles.clear()  # 이전 사각형 정보 초기화

        for idx, (x, y, w, h) in enumerate(self.last_face_positions):
            face_image = frame[y:y + h, x:x + w]

            try:
                result = DeepFace.find(face_image, db_path='faces', model_name='VGG-Face', enforce_detection=False)
                threshold = 0.4
                filtered_results = [res for res in result if res['distance'].values[0] < threshold]

                if len(filtered_results) > 0:
                    matched_face_path = filtered_results[0]['identity'].values[0]
                    self.last_detected_distances.append(filtered_results[0]['distance'].values[0])
                    self.last_detected_nicknames.append(self.get_nickname_from_filename(matched_face_path))
                    self.last_detected_rectangles.append(self.last_face_positions[idx])  # 초록색 사각형 정보 추가
                else:
                    self.last_detected_nicknames.append("unknown")
                    self.last_detected_distances.append(None)
                    self.last_detected_rectangles.append(None)  # 인식 실패 시 None 추가

            except Exception as e:
                print("Error in face recognition:", e)
                self.last_detected_nicknames.append("unknown")
                self.last_detected_distances.append(None)
                self.last_detected_rectangles.append(None)  # 인식 실패 시 None 추가

    async def recognize_emotion(self, frame):
        if self.last_face_positions is None:
            self.last_detected_emotions = ["unknown"]
            self.last_detected_emotion_scores = [{}]
            return

        self.last_detected_emotions.clear()
        self.last_detected_emotion_scores.clear()

        for (x, y, w, h) in self.last_face_positions:
            face_image = frame[y:y + h, x:x + w]

            try:
                emotion_result = DeepFace.analyze(face_image, actions=['emotion'], enforce_detection=False)
                if emotion_result:
                    self.last_detected_emotions.append(emotion_result[0]['dominant_emotion'])
                    self.last_detected_emotion_scores.append(emotion_result[0]['emotion'])
                else:
                    self.last_detected_emotions.append("unknown")
                    self.last_detected_emotion_scores.append({})

            except Exception as e:
                print("Error in emotion recognition:", e)
                self.last_detected_emotions.append("unknown")
                self.last_detected_emotion_scores.append({})

    def draw_faces(self, frame):
        if self.last_face_positions is None:
            return

        for idx, (x, y, w, h) in enumerate(self.last_face_positions):
            # 얼굴 감지 사각형 (노란색)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 노란색

            # 감정 정보가 있는지 확인하고 그리기
            if self.last_detected_emotions and idx < len(self.last_detected_emotions):
                emotion = self.last_detected_emotions[idx]
                if emotion:
                    scores = self.last_detected_emotion_scores[idx]
                    if scores:
                        sorted_emotions = sorted(scores.items(), key=lambda item: item[1], reverse=True)
                        top_emotion, top_score = sorted_emotions[0]
                        cv2.putText(frame, f"{top_emotion}: {top_score:.2f}%", (x + w + 10, y + 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)  # 빨간색

            # 인식된 얼굴에 대해서는 초록색 사각형
            if idx < len(self.last_detected_nicknames) and self.last_detected_nicknames[idx] != "unknown":
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색
            nickname = self.last_detected_nicknames[idx]
            distance = self.last_detected_distances[idx]

            if distance is not None:
                cv2.putText(frame, f"Detected: {nickname} ({distance:.2f})",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Detected: {nickname}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    def get_nickname_from_filename(self, filename):
        base_name = filename.split('/')[-1]  # 파일 경로에서 파일 이름만 추출
        name_part = base_name.split('.')[0]  # 확장자 제거
        name_part = name_part.split('(')[0].strip()  # 괄호 앞부분을 가져옴
        return name_part



# 사용 예시
async def main():
    face_recognition = FaceRecognition(
        registered_faces_folder='faces',
        model_prototxt='models/deploy.prototxt',
        model_weights='models/res10_300x300_ssd_iter_140000.caffemodel'
    )

    cap = cv2.VideoCapture(0)  # 웹캠에서 비디오 캡처

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_recognition.detect_faces(frame)  # 얼굴 감지
        await asyncio.gather(
            face_recognition.recognize_faces(frame),  # 얼굴 인식
            face_recognition.recognize_emotion(frame)  # 감정 인식
        )
        face_recognition.draw_faces(frame)  # 얼굴 및 감정 정보 그리기

        cv2.imshow("Face Recognition", frame)  # 결과 영상 표시

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
            break

    cap.release()
    cv2.destroyAllWindows()


# 메인 함수 실행
if __name__ == "__main__":
    asyncio.run(main())
