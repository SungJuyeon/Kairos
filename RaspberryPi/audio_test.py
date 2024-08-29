import paho.mqtt.client as mqtt
import sounddevice as sd
import numpy as np
import json

# MQTT 설정
broker = '3.27.221.93'  # MQTT 브로커 주소
topic = 'voice/data'

# 샘플링 주파수 및 채널 수
fs = 44100  # 샘플링 주파수
channels = 1  # 모노

# MQTT 클라이언트 설정 및 연결
client = mqtt.Client()
client.connect(broker)

# 음성 데이터 전송 함수
def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    # 인코딩된 음성 데이터를 JSON으로 변환
    audio_data_json = json.dumps(indata[:, 0].tolist())

    # MQTT로 데이터 전송
    client.publish(topic, audio_data_json)
    print("데이터 전송 완료")

# 음성 데이터 스트리밍 설정
with sd.InputStream(samplerate=fs, channels=channels, callback=audio_callback):
    print("음성 데이터 수집 및 전송 시작...")
    try:
        while True:
            sd.sleep(100)  # 계속 실행
    except KeyboardInterrupt:
        print("프로그램 종료")

# 연결 종료
client.disconnect()
