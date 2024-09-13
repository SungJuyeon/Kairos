import cv2
import numpy as np
import asyncio
# from ultralytics import YOLO  # YOLOv8 모델 로드

# model = YOLO('yolov8n.pt', verbose=False)  # YOLO 모델 로드
cap = cv2.VideoCapture(0)
current_density = 0.0

# def calculate_density(detections, frame):  # 밀도 계산 함수
#     height, width, _ = frame.shape
#     total_person_area = 0
#     for detection in detections:
#         if detection['name'] == "person" and detection['confidence'] > 0.5:
#             x, y, w, h = detection['box']
#             total_person_area += w * h
#     frame_area = height * width
#     density = total_person_area / frame_area
#     return density

async def update_frame():
    global current_density
    while True:
        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(0.1)
            continue

        # results = model(frame)  # 프레임에서 결과 얻기
        # detections = []
        # for result in results:
        #     for detection in result.boxes.data.cpu().numpy():
        #         x_min, y_min, x_max, y_max = detection[:4]
        #         confidence = detection[4]
        #         class_id = int(detection[5])
        #         if model.names[class_id] == "person" and confidence > 0.5:
        #             w = int(x_max - x_min)
        #             h = int(y_max - y_min)
        #             detections.append({
        #                 'box': [int(x_min), int(y_min), w, h],
        #                 'confidence': confidence,
        #                 'name': model.names[class_id]
        #             })

        # current_density = calculate_density(detections, frame)  # 밀도 계산
        await asyncio.sleep(0.0)
