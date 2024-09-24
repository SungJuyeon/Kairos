# mqtt_client.py
# MQTT 설정 및 메시지 처리를 위한 파일

import numpy as np
import json
import logging
import cv2
from gmqtt import Client as MQTTClient

# Logging 설정
logger = logging.getLogger(__name__)

# 상태 변수
distance_data = None
video_frames = []
speech_text = None
MAX_FRAMES = 3
current_speed = 50

# MQTT 설정
MQTT_BROKER = "223.194.157.85"
#MQTT_BROKER = "3.27.221.93"
#MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIOTOTEXT = "robot/audio_to_text"
MQTT_TOPIC_TEXTTOAUDIO = "robot/text_to_audio"
MQTT_TOPIC_HOME_CONTROL = "home/commands"
client = MQTTClient(client_id="fastapi_client")


async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    client.subscribe(MQTT_TOPIC_TEXTTOAUDIO) 
    logger.info("구독 완료")


async def on_message(client, topic, payload, qos, properties):
    global audio_data, distance_data, video_frames, speech_text

    # 비디오 데이터 처리
    if topic == MQTT_TOPIC_VIDEO:
        if len(video_frames) >= MAX_FRAMES:
            video_frames.pop(0)  # 가장 오래된 프레임 삭제
        img_encode = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
        video_frames.append(img_encode)
        #logger.info(f"Received video frame: {len(video_frames)}")
        return


    # 다른 데이터 처리
    try:
        message = json.loads(payload.decode('utf-8'))  # JSON 디코딩

        if topic == MQTT_TOPIC_DISTANCE:
            distance_data = message.get("distance")
            # logger.info(f"Distance data received: {distance_data}")
        # 음성 텍스트 처리
        elif topic == MQTT_TOPIC_TEXTTOAUDIO:
            speech_text = message.get("speech_text")
            logger.info(f"Received speech text: {speech_text}")
            # 텍스트를 GPT에 전달하는 함수 실행##################################
    except Exception as e:
        logger.error(f"Error processing message on topic {topic}: {e}")

    

    return


async def setup_mqtt():
    client.on_message = on_message
    await on_connect()


async def move(direction: str):
    logger.info(f"Attempting to move {direction}")
    command = json.dumps({"command": direction})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logger.info(f"Command sent: {command}")


async def speed(action):
    global current_speed
    logger.info(f"Attempting to set speed: {action}")
    if action == "up":
        current_speed = min(100, current_speed + 10)  # 속도를 10 증가, 최대 100으로 제한
    elif action == "down":
        current_speed = max(0, current_speed - 10)  # 속도를 10 감소, 최소 0으로 제한
    elif action >=0 and action <=100:
        current_speed = action
    else:
        logger.warning(f"Invalid action for speed: {action}")
        return {"error": "Invalid action"}, 400

    command = json.dumps({"command": "set_speed", "speed": current_speed})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logger.info(f"Speed command sent: {command}")
    return {"message": "Speed command sent successfully", "current_speed": current_speed}

async def text_to_audio(text):
    command = json.dumps({"command": "text_to_audio", "text": text})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logger.info(f"Text to speech command sent: {command}")
    return {"message": "Text to speech command sent successfully"}

async def home_control(device, state):
    command = json.dumps({"command": "home_control", "device": device, "state": state})
    client.publish(MQTT_TOPIC_HOME_CONTROL, command)
    logger.info(f"Home control command sent: {command}")
    return {"message": "Home control command sent successfully"}

