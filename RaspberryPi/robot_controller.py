import asyncio
import logging
import json
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
import video
import ultrasonic
import motor_control
import audio_text

logging.basicConfig(level=logging.INFO)

# MQTT 설정
MQTT_BROKER = "3.27.221.93"  # MQTT 브로커 주소 입력
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "robot/commands"
MQTT_TOPIC_DISTANCE = "robot/distance"
MQTT_TOPIC_VIDEO = "robot/video"
MQTT_TOPIC_AUDIOTOTEXT = "robot/audio_to_text"
MQTT_TOPIC_TEXTTOAUDIO = "robot/text_to_audio"

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
            await asyncio.sleep(2)  # 재시도 대기


@asynccontextmanager
async def lifespan():
    client.on_message = on_message
    await on_connect()

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
        logging.info("Interrupted by user")
    finally:
        loop.close()
