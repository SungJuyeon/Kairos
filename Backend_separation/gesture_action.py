# gesture_action.py
# 손동작 관련 명령을 처리하는 파일

import asyncio
import time
import logging
from mqtt_client import move, speed, distance_data

logger = logging.getLogger(__name__)

# 상태 변수
last_command_time = 0
command_cooldown = 10  # 10초 쿨다운

async def gesture_action(action):
    global last_command_time
    current_time = time.time()

    # 쿨다운 체크
    if current_time - last_command_time < command_cooldown:
        logger.info("명령이 쿨다운 중입니다. 동작을 무시합니다.")
        return

    if action == 'come':
        await speed(80)
        await move("forward")
        logger.info("명령 전송: 전진")
        last_command_time = current_time
        while True:
            if distance_data is not None and distance_data < 10:
                await move("stop_wheel")
                break
            await asyncio.sleep(0.1)

    elif action == 'spin':
        await speed(100)
        await move("right")
        logger.info("명령 전송: 우회전")
        last_command_time = current_time
        await asyncio.sleep(2)
        await move("stop_wheel")

    elif action == 'away':
        await speed(80)
        await move("back")
        logger.info("명령 전송: 후진")
        last_command_time = current_time
        await asyncio.sleep(2)
        await move("stop_wheel")