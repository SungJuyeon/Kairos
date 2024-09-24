# mqtt_client.py
# MQTT 설정 및 메시지 처리를 위한 파일

import numpy as np
import json
import logging
import cv2
from gmqtt import Client as MQTTClient

from GPT.openai_api import process_user_input

# Logging 설정
logger = logging.getLogger(__name__)

# 상태 변수
distance_data = None
video_frames = []
audio_data = []
MAX_FRAMES = 3
current_speed = 50

# MQTT 설정
MQTT_BROKER = "3.27.221.93"
#MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_SPEECH = "robot/speech"
MQTT_TOPIC_TEXT = "robot/text"

client = MQTTClient(client_id="fastapi_client")


async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    #client.subscribe(MQTT_TOPIC_DISTANCE)
    #client.subscribe(MQTT_TOPIC_VIDEO)
    client.subscribe(MQTT_TOPIC_SPEECH)  # 음성 텍스트 토픽 구독
    logger.info("구독 완료")


async def on_message(client, topic, payload, qos, properties):
    global audio_data, distance_data, video_frames
    # 비디오 데이터 처리

    try:
        message = json.loads(payload.decode('utf-8'))  # JSON 디코딩

        if topic == MQTT_TOPIC_DISTANCE:
            distance_data = message.get("distance")
            # logger.info(f"Distance data received: {distance_data}")
        # 음성 텍스트 처리
        elif topic == MQTT_TOPIC_SPEECH:
            speech_text = message.get("text")
            logger.info(f"Received speech text: {speech_text}")
            command = {"command": "text_to_speech", "text": speech_text}
            # 텍스트를 GPT에 전달하고 결과를 얻음
            response_text = process_user_input(speech_text)
            if response_text:  # response_text가 None이 아닌 경우
                await text_to_speech(response_text)
            else:
                logger.warning("No response text received from process_user_input.")

    except Exception as e:
        logger.error(f"Error processing message on topic {topic}: {e}")



async def setup_mqtt():
    client.on_message = on_message
    await on_connect()

async def text_to_speech(text):
    if client is None:  # client가 None인지 확인
        logging.error("MQTT client is not initialized.")
        return
    command = json.dumps({"command": "text_to_speech", "text": text})
    client.publish(MQTT_TOPIC_COMMAND, command)
    logging.info(f"Text to speech command sent: {command}")
    return {"message": "Text to speech command sent successfully"}
