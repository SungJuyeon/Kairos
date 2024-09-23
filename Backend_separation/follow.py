import time
import cv2
import numpy as np
import asyncio
from ultralytics import YOLO
from mqtt_client import move, speed, video_frames, distance_data

model = YOLO('yolov8n.pt', verbose=False)  # YOLO 모델 로드

async def follow():
    # 속도 설정 및 왼쪽으로 회전 시작
    await speed(40)
    await move("left")
    
    start_time = time.time()
    person_detected = False

    while True:
        # 5초 경과 또는 사람 감지 시 루프 종료
        if time.time() - start_time > 5 or person_detected:
            await move("stop")  # 움직임 멈춤
            break

        # 최신 프레임 가져오기
        if video_frames:
            frame = video_frames[-1]
            # 사람 감지 함수 호출
            person_detected, bbox, position = detect_person(frame)
            if person_detected:
                # 네모 박스 그리기
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        await asyncio.sleep(0.1)  # 잠시 대기

    # 사람 추적 시작
    while True:
        # 거리 데이터 업데이트
        current_distance = distance_data

        if video_frames:
            frame = video_frames[-1]
            person_detected, bbox, position = detect_person(frame)

            if not person_detected:
                # 사람을 찾지 못하면 회전하여 다시 찾기
                await move("left")
                await asyncio.sleep(0.5)
                continue
            else:
                # 사람의 위치에 따라 이동 조정
                if position == "center":
                    await move("forward")
                    if current_distance and current_distance <= 30:
                        await move("stop_wheel")
                        await move("stop_actuator")
                        break
                elif position == "left":
                    await move("left")
                elif position == "right":
                    await move("right")
                elif position == "up":
                    await move("up")
                elif position == "down":
                    await move("down")
        await asyncio.sleep(0.1)

def detect_person(frame):
    # YOLOv8을 사용하여 사람 감지
    results = model.predict(frame)
    detections = results[0].boxes

    if detections:
        # 사람 클래스만 필터링 (클래스 ID 0은 'person'을 나타냅니다)
        for detection in detections:
            if int(detection.cls[0]) == 0:
                x1, y1, x2, y2 = detection.xyxy[0]
                x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)

                frame_center_x = frame.shape[1] / 2
                frame_center_y = frame.shape[0] / 2
                person_center_x = x + w / 2
                person_center_y = y + h / 2

                # 위치 판단
                if abs(person_center_x - frame_center_x) < frame.shape[1] * 0.1:
                    horizontal_position = "center"
                elif person_center_x < frame_center_x:
                    horizontal_position = "left"
                else:
                    horizontal_position = "right"

                if abs(person_center_y - frame_center_y) < frame.shape[0] * 0.1:
                    vertical_position = "center"
                elif person_center_y < frame_center_y:
                    vertical_position = "up"
                else:
                    vertical_position = "down"

                # 우선 수평 위치를 기준으로 반환
                if horizontal_position == "center" and vertical_position == "center":
                    position = "center"
                elif horizontal_position != "center":
                    position = horizontal_position
                else:
                    position = vertical_position

                return True, (x, y, w, h), position
        return False, None, None
    else:
        return False, None, None

# 비디오 프레임 생성기
async def generate_video_frames():
    while True:
        if video_frames:
            frame = video_frames[-1].copy()  # 프레임 복사
            person_detected, bbox, position = detect_person(frame)
            if person_detected:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 프레임을 JPEG로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # 멀티파트 응답 생성
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            await asyncio.sleep(0.1)
        else:
            # 프레임이 없으면 잠시 대기
            time.sleep(0.1)