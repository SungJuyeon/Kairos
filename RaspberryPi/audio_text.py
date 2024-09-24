# 음성 캡처 큐
import os
import queue
import pyttsx3
import speech_recognition as sr
import asyncio
import concurrent.futures
import json
import logging
import pyttsx3


audio_queue = queue.Queue()

recognizer = sr.Recognizer()

send_audio_task = None

async def start_send_audio(client):
    global send_audio_task
    send_audio_task = asyncio.create_task(send_audio(client))

async def stop_send_audio():
    global send_audio_task
    if send_audio_task:
        send_audio_task.cancel()
        send_audio_task = None

async def send_audio(client):
    while True:
        try:
            text = await audio_to_text()
            if text:
                speech_message = json.dumps({"text": text})
                from robot_controller import MQTT_TOPIC_AUDIOTOTEXT
                client.publish(MQTT_TOPIC_AUDIOTOTEXT, speech_message)
                logging.info(f"음성 텍스트 발행: {text}")
        except Exception as e:
            logging.error(f"send_speech_text 오류: {e}")
        finally:
            await asyncio.sleep(1)  # 1초 대기 후 다시 음성 인식 시작

async def audio_to_text():
    loop = asyncio.get_event_loop()
    with sr.Microphone() as source:
        print("음성을 듣고 있습니다... (2~10초)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                audio = await loop.run_in_executor(pool, lambda: recognizer.listen(source, timeout=2, phrase_time_limit=10))
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


# 글로벌 엔진 객체 생성
engine = pyttsx3.init()

# 음성 속성 설정 (시스템에 맞는 음성 선택)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak_blocking(text):
    engine.say(text)
    engine.runAndWait()

async def text_to_audio(text, lang='ko'):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, speak_blocking, text)