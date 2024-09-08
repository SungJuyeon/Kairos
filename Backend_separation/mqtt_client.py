# mqtt_client.py
import asyncio
import json
import logging
from gmqtt import Client as MQTTClient

# Logging 설정
logger = logging.getLogger(__name__)

# MQTT 설정
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIO = "robot/audio"

client = MQTTClient(client_id="fastapi_client")

async def on_connect():
    await client.connect(MQTT_BROKER, MQTT_PORT)
    logger.info("연결: MQTT Broker")
    client.subscribe(MQTT_TOPIC_DISTANCE)
    client.subscribe(MQTT_TOPIC_VIDEO)
    client.subscribe(MQTT_TOPIC_AUDIO)
    logger.info("구독 완료")

async def on_message(client, topic, payload, qos, properties):
    # 메시지 처리 로직은 app.py에서 처리하도록 변경
    pass

async def setup_mqtt():
    client.on_message = on_message
    await on_connect()
