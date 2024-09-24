import asyncio
import time
import logging
import json
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
import sounddevice as sd
import speech_recognition as sr
import concurrent.futures
from gtts import gTTS
import os

from playsound import playsound


cap = cv2.VideoCapture(0)
# 음성 캡처 큐
audio_queue = queue.Queue()



# 로깅 설정
logging.basicConfig(level=logging.INFO)



recognizer = sr.Recognizer()

async def recognize_speech():
    loop = asyncio.get_event_loop()
    with sr.Microphone() as source:
        print("음성을 듣고 있습니다... (10초 동안)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                audio = await loop.run_in_executor(pool, lambda: recognizer.listen(source, timeout=10))
            print("음성 인식 중...")
            with concurrent.futures.ThreadPoolExecutor() as pool:
                text = await loop.run_in_executor(pool, lambda: recognizer.recognize_google(audio, language="ko-KR"))
            print(f"인식된 텍스트: {text}")
            return text
        except sr.WaitTimeoutError:
            print("음성 입력 시간이 초과되었습니다.")
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print(f"음성 인식 서비스 오류: {e}")
        except Exception as e:
            print(f"예상치 못한 오류 발생: {e}")
    return None

async def send_speech_text(client):
    while True:
        try:
            text = await recognize_speech()
            if text:
                speech_message = json.dumps({"text": text})
                client.publish(MQTT_TOPIC_SPEECH, speech_message)
                logging.info(f"음성 텍스트 발행: {text}")
        except Exception as e:
            logging.error(f"send_speech_text 오류: {e}")
        finally:
            await asyncio.sleep(5)  # 1초 대기 후 다시 음성 인식 시작


#############################################################################
def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    #os.system("start output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")

# MQTT 설정
MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소 입력

# GPIO를 사용하는 모듈 대신 Mock 클래스 작성
class motor_control:
    @staticmethod
    def wheel_control(direction):
        logging.info(f"모의 모터 제어: 방향 {direction}")

    @staticmethod
    def set_speed(speed=50):
        logging.info(f"모의 모터 속도 설정: 속도 {speed}")

    @staticmethod
    def actuator_control(direction):
        logging.info(f"모의 액추에이터 제어: 방향 {direction}")

class ultrasonic:
    send_distance_task = None

    @staticmethod
    async def start_send_distance(client):
        logging.info("모의 거리 전송 시작")
        ultrasonic.send_distance_task = asyncio.create_task(ultrasonic.mock_send_distance(client))

    @staticmethod
    async def stop_send_distance():
        if ultrasonic.send_distance_task:
            ultrasonic.send_distance_task.cancel()
            ultrasonic.send_distance_task = None
            logging.info("모의 거리 전송 중지")

    @staticmethod
    async def mock_send_distance(client):
        while True:
            await asyncio.sleep(1)
            distance = 100  # 모의 거리 값
            distance_message = json.dumps({"distance": distance})
            MQTT_TOPIC_DISTANCE = "robot/distance"
            client.publish(MQTT_TOPIC_DISTANCE, distance_message)
            logging.info(f"모의 거리 발행: {distance}")

import audio_text
import video
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)

# MQTT 설정
MQTT_BROKER = "localhost"
#MQTT_BROKER = "3.27.221.93"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
#########juyeon
# MQTT_TOPIC_SPEECH = "robot/speech"
# MQTT_TOPIC_TEXT = "robot/text"
######hanbin2
MQTT_TOPIC_AUDIOTOTEXT = "robot/audio_to_text"
MQTT_TOPIC_TEXTTOAUDIO = "robot/text_to_audio"

client = MQTTClient(client_id="robot_controller")

async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logging.info("MQTT 브로커에 연결되었습니다.")
    client.subscribe(MQTT_TOPIC_COMMAND)
    logging.info(f"명령어 토픽 구독: {MQTT_TOPIC_COMMAND}")

async def on_message(client, topic, payload, qos, properties):
    command = json.loads(payload.decode('utf-8'))
    logging.info(f"명령 수신: {command}")

    if command["command"] in ["forward", "back", "left", "right", "stop_wheel"]:
        motor_control.wheel_control(command["command"])
    elif command["command"] in ["up", "down", "stop_actuator"]:
        motor_control.actuator_control(command["command"])
    elif command["command"] == "set_speed":
        motor_control.set_speed(command["speed"]) 

    elif command["command"] == "start_send_distance":
        await ultrasonic.start_send_distance(client)
    elif command["command"] == "stop_send_distance":
        await ultrasonic.stop_send_distance()

    elif command["command"] == "start_generate_frames":
        await video.start_generate_frames(client)
    elif command["command"] == "stop_generate_frames":
        await video.stop_generate_frames()

    elif command["command"] == "start_send_audio":
        await audio_text.start_send_audio(client)
    elif command["command"] == "stop_send_audio":
        await audio_text.stop_send_audio()
    elif command["command"] == "text_to_audio":
        await audio_text.text_to_audio(command["text"])

    # elif command.get("command") == "text_to_speech":
    #     text_to_speech(command["text"])

    else:
        logging.warning(f"잘못된 명령: {command}")

async def on_disconnect():
    logging.warning("MQTT 브로커와의 연결이 끊어졌습니다. 재연결 시도 중...")
    while True:
        try:
            await client.connect(MQTT_BROKER, MQTT_PORT)
            logging.info("MQTT 브로커에 재연결되었습니다.")
            break
        except Exception as e:
            logging.error(f"재연결 실패: {e}")
            await asyncio.sleep(2)

@asynccontextmanager
async def lifespan():
    client.on_message = on_message
    await on_connect()
    asyncio.create_task(send_speech_text(client))
    #############3juyeon
    #await ultrasonic.start_send_distance(client)

    await video.start_generate_frames(client)
    # await audio_text.start_send_audio(client)
    yield
    logging.info("프로그램을 종료합니다.")
    await client.disconnect()

async def main():
    async with lifespan():
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        # asyncio.run(main())
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("사용자에 의해 중단되었습니다.")
    finally:
        loop.close()
        
