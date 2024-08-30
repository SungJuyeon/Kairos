from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2

app = FastAPI()

def generate_frames():
    cap = cv2.VideoCapture(0)  # 웹캠 사용
    while True:
        success, frame = cap.read()  # 프레임 읽기
        if not success:
            break
        else:
            # 프레임을 JPEG로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  # 바이트로 변환
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # HTTP 스트리밍 포맷

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)