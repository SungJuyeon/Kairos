from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import paho.mqtt.client as mqtt
import json
import sounddevice as sd
import numpy as np
import threading

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

audio_data = None

# MQTT 설정
broker = '3.27.221.93'
topic = 'voice/data'

# 음성을 재생하는 함수
def play_audio():
    global audio_data
    while True:
        if audio_data is not None:
            sd.play(audio_data, samplerate=44100)
            sd.wait()  # 재생이 완료될 때까지 대기

# MQTT 메시지를 수신하는 콜백 함수
def on_message(client, userdata, message):
    global audio_data
    audio_data = np.array(json.loads(message.payload.decode()), dtype='float32')

# MQTT 클라이언트 설정
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(broker)
mqtt_client.subscribe(topic)
mqtt_client.loop_start()

# 별도의 스레드에서 음성을 재생
threading.Thread(target=play_audio, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>음성 데이터 스트리밍</title>
    </head>
    <body>
        <h1>음성 데이터 수신 중...</h1>
    </body>
    </html>
    """

@app.get("/audio")
async def get_audio():
    return audio_data.tolist() if audio_data is not None else []

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
