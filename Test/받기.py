from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import paho.mqtt.client as mqtt
import io
import wave
import uvicorn

app = FastAPI()

# 오디오 버퍼
audio_buffer = io.BytesIO()

# WAV 파일 저장을 위한 파일 경로
wav_file_path = "received_audio.wav"

# MQTT 콜백 함수
def on_message(client, userdata, message):
    print(f"Received message with length: {len(message.payload)} bytes")  # 수신된 데이터 길이 출력
    print(f"Received PCM Data: {message.payload[:100]}")
    if len(message.payload) > 0:  # 데이터가 유효한 경우에만 처리
        audio_buffer.seek(0)

        # WAV 파일로 변환하여 저장
        with wave.open(wav_file_path, 'wb') as wf:
            wf.setnchannels(1)  # 모노
            wf.setsampwidth(2)  # 16비트
            wf.setframerate(16000)  # 샘플링 레이트
            wf.writeframes(message.payload)  # PCM 데이터를 WAV에 작성

        # 버퍼에 저장
        audio_buffer.write(message.payload)
        audio_buffer.truncate()  # 버퍼를 비웁니다 (이전 데이터 삭제)

# MQTT 클라이언트 설정
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect('localhost')
mqtt_client.subscribe('audio_feed')
mqtt_client.loop_start()

@app.get("/audio_feed")
async def audio_feed():
    audio_buffer.seek(0)  # 버퍼의 시작으로 이동
    return StreamingResponse(audio_buffer, media_type="audio/wav")

# FastAPI 애플리케이션 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
