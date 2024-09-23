import queue
import cv2
import asyncio
import RPi.GPIO as GPIO
import time
import logging
import json
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
import sounddevice as sd
import motor_control as mc
import speech_recognition as sr
import concurrent.futures
from gtts import gTTS
import os

# 핀 번호 설정

ULTRASONIC_PINS = {
    'TRIG': 20,
    'ECHO': 16
}

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(ULTRASONIC_PINS['TRIG'], GPIO.OUT)
GPIO.setup(ULTRASONIC_PINS['ECHO'], GPIO.IN)



# 카메라 설정
cap = cv2.VideoCapture(0)
# 음성 캡처 큐
audio_queue = queue.Queue()



# 로깅 설정
logging.basicConfig(level=logging.INFO)




# 거리 전송 ###################################################################
async def send_distance(client):
    while True:
        try:
            distance = measure_distance()
            if distance is not None:
                distance_message = json.dumps({"distance": distance})
                client.publish(MQTT_TOPIC_DISTANCE, distance_message)
                #logging.info(f"거리 발행: {distance}")
            else:
                logging.warning("거리 측정 실패")
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(f"send_distance 오류: {e}")
            await asyncio.sleep(1)


def measure_distance():
    try:
        GPIO.output(ULTRASONIC_PINS['TRIG'], True)
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_PINS['TRIG'], False)

        pulse_start = time.time()
        pulse_end = pulse_start
        timeout = time.time() + 0.1

        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                raise Exception("Echo 시작 타임아웃")

        while GPIO.input(ULTRASONIC_PINS['ECHO']) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                raise Exception("Echo 종료 타임아웃")

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)
    except Exception as e:
        logging.error(f"거리 측정 오류: {e}")
        return None


#############################################################################


# 영상 전송 ####################################################################
async def generate_frames(client):
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to capture frame")
                await asyncio.sleep(0.05)  # 프레임 캡처 실패 시 대기
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            client.publish(MQTT_TOPIC_VIDEO, frame_data)  # 비디오 프레임 전송
            # logging.info("Sent a video frame")

            await asyncio.sleep(0.05)  # 전송 주기 조정
        except Exception as e:
            logging.error(f"Error in generate_frames: {e}")
            await asyncio.sleep(1)  # 오류 발생 시 대기
    stream.stop()




# 음성 인식을 위한 recognizer 객체 생성#############################3
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
                speech_message = json.dumps({"speech_text": text})
                client.publish(MQTT_TOPIC_SPEECH, speech_message)
                logging.info(f"음성 텍스트 발행: {text}")
        except Exception as e:
            logging.error(f"send_speech_text 오류: {e}")
        finally:
            await asyncio.sleep(1)  # 1초 대기 후 다시 음성 인식 시작


#############################################################################
def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    os.system("afplay output.mp3")
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
    logging.info("구독")


async def on_message(client, topic, payload, qos, properties):
    command = json.loads(payload.decode('utf-8'))
    logging.info(f"Received command: {command}")

    if command["command"] in ["forward", "back", "left", "right", "stop_wheel"]:
        mc.wheel_control(command["command"])
    elif command["command"] in ["up", "down", "stop_actuator"]:
        mc.actuator_control(command["command"])
    elif command["command"] == "set_speed":
        mc.set_speed(command["speed"])  # 속도 조절 명령 처리
    elif command["command"] == "text_to_speech":
        text_to_speech(command["text"])
    else:
        logging.warning(f"Invalid command: {command}")


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

    # 비동기 작업 시작
    #asyncio.create_task(send_distance(client))
    #asyncio.create_task(generate_frames(client))
    #asyncio.create_task(send_speech_text(client))  # 음성 인식 태스크 추가

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
        # 종료 처리
        GPIO.cleanup()
        cap.release()
        logging.info("Cleanup completed")
