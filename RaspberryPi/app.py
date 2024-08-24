from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import threading
from motor_controller import motor_control, stop  # 모터 제어 모듈 임포트
from cam import generate_frames  # 카메라 모듈 임포트

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

motor_thread = None  # 모터 동작 스레드 저장

@app.post("/move/{direction}")
def move(direction: str):
    global motor_thread
    if motor_thread is not None and motor_thread.is_alive():
        stop()  # 현재 모터가 동작 중이면 정지

    motor_thread = threading.Thread(target=motor_control, args=(direction,))
    motor_thread.start()
    return {"message": f"Moving {direction}"}

@app.post("/stop")
def stop_motors():
    stop()
    return {"message": "Stopped"}

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# @app.get("/density")
# async def get_density():
#     return {"density": current_density}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
