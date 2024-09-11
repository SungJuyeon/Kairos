# gesture_action.py
# 손동작 관련 명령을 처리하는 파일

import json
import time
import logging

logger = logging.getLogger(__name__)

# 상태 변수
last_command_time = 0
command_cooldown = 10  # 10초 쿨다운


async def gesture_action(action, client, distance_data):
    global last_command_time
    current_time = time.time()

    if current_time - last_command_time < command_cooldown:
        logger.info("Command is on cooldown. Ignoring action.")
        return

    if action == 'come':
        command = json.dumps({"command": "forward"})
        client.publish("robot/commands", command)
        logger.info("Command sent: forward")
        last_command_time = current_time
        # 추가 로직...
    elif action == 'spin':
        # 추가 로직...
        pass
    elif action == 'away':
        # 추가 로직...
        pass
