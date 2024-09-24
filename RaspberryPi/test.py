import queue
import cv2
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
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_SPEECH = "robot/speech"
MQTT_TOPIC_TEXT = "robot/text"

client = MQTTClient(client_id="robot_controller")


async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logging.info("연결")
    client.subscribe(MQTT_TOPIC_COMMAND)
    client.subscribe(MQTT_TOPIC_SPEECH)
    client.subscribe(MQTT_TOPIC_TEXT)
    logging.info("구독")


async def on_message(client, topic, payload, qos, properties):
    try:
        command = json.loads(payload.decode('utf-8'))
        logging.info(f"Received command: {command}")

        if command.get("command") == "text_to_speech":
            text_to_speech(command["text"])
        else:
            logging.warning(f"Invalid command: {command}")
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from payload.")
    except Exception as e:
        logging.error(f"Error in message handling: {e}")



async def on_disconnect():
    logging.warning("Disconnected from MQTT broker, attempting to reconnect...")
    while True:
        try:
            await client.connect(MQTT_BROKER, MQTT_PORT)
            logging.info("Reconnected to MQTT broker")
            break
        except Exception as e:
            logging.error(f"Reconnect failed: {e}")
            await asyncio.sleep(5)  # 재시도 대기

@asynccontextmanager
async def lifespan():
    client.on_message = on_message
    await on_connect()
    asyncio.create_task(send_speech_text(client))
    yield

    logging.info("종료")
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
        logging.info("Interrupted by user, cleaning up...")
    finally:
        #GPIO.cleanup()
        #cap.release()
        loop.close()