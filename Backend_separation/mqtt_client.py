# mqtt_client.py
# MQTT 설정 및 메시지 처리를 위한 파일

import asyncio
import json
import logging
import cv2
from gmqtt import Client as MQTTClient

# Logging 설정
logger = logging.getLogger(__name__)

# MQTT 설정
# MQTT_BROKER = "3.27.221.93"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

client = MQTTClient(client_id="fastapi_client")

# 상태 변수
distance_data = None
audio_data = []
video_frames = []


async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    client.subscribe(MQTT_TOPIC_AUDIO)
    logger.info("구독 완료")


async def on_message(client, topic, payload, qos, properties):
    global audio_data, distance_data, video_frames

    # 비디오 데이터 처리
    if topic == MQTT_TOPIC_VIDEO:
        import numpy as np
        img_encode = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
        video_frames.append(img_encode)

        # 최대 프레임 수를 초과하면 가장 오래된 프레임 제거
        from Backend_separation.video_processing import MAX_VIDEO_FRAMES
        if len(video_frames) > MAX_VIDEO_FRAMES:
            video_frames.pop(0)
        return

    # 오디오 데이터 처리
    elif topic == MQTT_TOPIC_AUDIO:
        audio_data.append(payload)  # 오디오 데이터는 바이너리로 처리
        return

    # 거리 데이터 처리
    try:
        message = json.loads(payload.decode('utf-8'))  # JSON 디코딩
        if topic == MQTT_TOPIC_DISTANCE:
            distance_data = message.get("distance")
            logger.info(f"Distance data received: {distance_data}")
    except json.JSONDecodeError:
        logger.error(f"Received non-JSON message on topic {topic}")
    except Exception as e:
        logger.error(f"Error processing message on topic {topic}: {e}")


async def setup_mqtt():
    client.on_message = on_message
    await on_connect()
