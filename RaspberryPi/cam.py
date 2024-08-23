# cam.py
import cv2
import asyncio

cap = cv2.VideoCapture(0)

async def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # JPEG 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        await asyncio.sleep(0.01)  # CPU 사용량 조절을 위한 대기
