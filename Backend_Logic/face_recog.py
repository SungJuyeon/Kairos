import face_recognition
import cv2
import numpy as np
import os

class FaceRecog:
    def __init__(self):
        # 등록된 얼굴의 인코딩과 이름을 저장할 리스트 초기화
        self.known_face_encodings = []
        self.known_face_names = []

        # 등록된 얼굴 이미지가 있는 디렉토리
        dirname = 'registered_faces'
        files = os.listdir(dirname)  # 디렉토리 내 모든 파일을 리스트로 가져옴
        for filename in files:
            name, ext = os.path.splitext(filename)  # 파일 이름과 확장자로 분리
            if ext.lower() == '.jpg':  # .jpg 확장자의 파일만 처리
                self.known_face_names.append(name)  # 얼굴의 이름을 저장
                pathname = os.path.join(dirname, filename)  # 이미지 파일의 전체 경로
                img = face_recognition.load_image_file(pathname)  # 이미지 파일 로드
                face_encodings = face_recognition.face_encodings(img)  # 얼굴 인코딩을 추출
                if face_encodings:  # 얼굴 인코딩이 있는 경우
                    self.known_face_encodings.append(face_encodings[0])  # 첫 번째 얼굴 인코딩을 저장

        # 현재 프레임의 얼굴 위치, 인코딩, 이름을 저장할 리스트 초기화
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True  # 매 프레임을 처리할지 여부를 나타내는 플래그

    def get_frame(self, frame):
        # 프레임을 원래 크기의 1/4로 축소하여 처리 속도 향상
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # BGR 이미지를 RGB로 변환 (face_recognition 라이브러리에서 요구)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 매 프레임마다 처리하여 성능 최적화
        if self.process_this_frame:
            # 현재 프레임에서 모든 얼굴 위치 찾기
            self.face_locations = face_recognition.face_locations(rgb_small_frame)

            # 현재 프레임에서 모든 얼굴 인코딩 찾기
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []  # 현재 프레임의 얼굴 이름을 저장할 리스트 초기화
            for face_encoding in self.face_encodings:
                # 얼굴 인코딩을 등록된 얼굴 인코딩과 비교
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                if distances.size > 0:  # 비교할 거리가 있는 경우
                    min_value = min(distances)  # 최소 거리 값 찾기
                    name = "Unknown"  # 기본 이름을 "Unknown"으로 설정

                    # 최소 거리가 임계값보다 작으면 얼굴을 매칭
                    if min_value < 0.6:
                        index = np.argmin(distances)  # 가장 가까운 매칭의 인덱스 찾기
                        name = self.known_face_names[index]  # 매칭된 얼굴의 이름 가져오기

                else:
                    name = "Unknown"  # 거리가 없으면 "Unknown"으로 설정

                self.face_names.append(name)  # 얼굴 이름 리스트에 추가

        self.process_this_frame = not self.process_this_frame  # 프레임 처리 플래그를 토글

        # 프레임에 사각형과 레이블 그리기
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # 얼굴 위치를 원래 크기로 스케일 업
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 얼굴 주위에 사각형 그리기
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 얼굴 아래에 이름 레이블 그리기
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX  # 글꼴 유형 선택
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)  # 텍스트 레이블 추가

        return frame, self.face_names  # 수정된 반환값
