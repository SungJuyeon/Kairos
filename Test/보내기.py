import sounddevice as sd
import numpy as np
import paho.mqtt.client as mqtt
import time

# MQTT 설정
MQTT_BROKER = 'localhost'
MQTT_TOPIC = 'audio_feed'

# 오디오 설정
SAMPLE_RATE = 16000  # 샘플링 레이트
CHANNELS = 1         # 채널 수
CHUNK = 2048         # 청크 크기

# 사용할 오디오 장치의 인덱스
DEVICE_INDEX = 3  # "MacBook Air 마이크"의 인덱스

# MQTT 클라이언트 초기화
client = mqtt.Client()
client.connect(MQTT_BROKER)

# 음성 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    print(f"Sending {frames} frames of data: {indata[:5]}")  # 수집된 데이터의 첫 5개 샘플 출력
    # 데이터를 MQTT로 전송
    client.publish(MQTT_TOPIC, indata.tobytes())

# 음성 스트리밍 시작
with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, blocksize=CHUNK, device=DEVICE_INDEX):
    print("음성을 수집 중입니다. 종료하려면 Ctrl+C를 누르세요.")
    while True:
        time.sleep(1)  # 메인 스레드를 유지하기 위해
