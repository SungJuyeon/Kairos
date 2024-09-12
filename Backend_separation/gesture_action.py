# gesture_action.py
# 손동작 관련 명령을 처리하는 파일

import json
import time
import logging

logger = logging.getLogger(__name__)

MQTT_TOPIC_COMMAND = "robot/commands"

# 상태 변수
last_command_time = 0
command_cooldown = 10  # 10초 쿨다운


async def gesture_action(action, client, distance_data):
    global last_command_time  # 마지막 명령 발행 시간 사용
    current_time = time.time()  # 현재 시간 가져오기

    # 쿨다운 체크
    if current_time - last_command_time < command_cooldown:
        logger.info("Command is on cooldown. Ignoring action.")
        return  # cooldown 지나지 않았으면 명령 무시

    if action == 'come':
        command = json.dumps({"command": "forward"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: forward")
        last_command_time = current_time  # 명령 발행 시간 기록
        while True:
            if distance_data is not None and distance_data < 10:
                command = json.dumps({"command": "stop"})
                client.publish(MQTT_TOPIC_COMMAND, command)
                break
            await asyncio.sleep(0.1)  # 0.1초 대기하여 CPU 사용량을 줄임

    elif action == 'spin':
        command = json.dumps({"command": "right"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: right")
        last_command_time = current_time  # 명령 발행 시간 기록
        await asyncio.sleep(2)
        command = json.dumps({"command": "stop"})
        client.publish(MQTT_TOPIC_COMMAND, command)

    elif action == 'away':
        command = json.dumps({"command": "back"})
        client.publish(MQTT_TOPIC_COMMAND, command)
        logger.info("Command sent: back")
        last_command_time = current_time  # 명령 발행 시간 기록
        await asyncio.sleep(2)
        command = json.dumps({"command": "stop"})
        client.publish(MQTT_TOPIC_COMMAND, command)