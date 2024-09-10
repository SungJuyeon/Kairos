import asyncio
import json
import logging
from contextlib import asynccontextmanager
import cv2
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from gmqtt import Client as MQTTClient
import numpy as np
from Backend_Logic.FaceRecognotion import FaceRecognition
from Backend_Logic.HandGestureRecognizer import HandGestureRecognizer
import time




# # 손동작 인식기 인스턴스 생성
# try:
#     gesture_recognizer = HandGestureRecognizer(model_path='./models/model.keras')
# except Exception as e:
#     logger.error(f"손동작 모델 로드 중 오류 발생: {e}")







async def on_message(client, topic, payload, qos, properties):
     try:
        message = json.loads(payload.decode('utf-8'))  # JSON 디코딩


        elif topic == MQTT_TOPIC_COMMAND:
            audio_data = message["audio"]
            logger.info("Received audio data")



@asynccontextmanager
async def lifespan(app: FastAPI):
    client.on_message = on_message
    await on_connect()
    # 비동기 작업
    asyncio.create_task(video_frame_updater())
    yield
    logger.info("종료")
    await client.disconnect()









async def video_frame_updater():
    global video_frames
    logger.info("비디오 프레임 업데이터 시작")
    while True:
        try:
            if len(video_frames) > 0:  # 리스트가 비어 있지 않은 경우
                current_frame = video_frames[0]  # 첫 번째 프레임 가져오기
                await asyncio.to_thread(face_recognition.detect_faces, current_frame)
                await asyncio.to_thread(face_recognition.recognize_emotion, current_frame)
                await asyncio.to_thread(face_recognition.recognize_faces, current_frame)
            else:
                logger.info("프레임이 없습니다.")
            await asyncio.sleep(1)  # 너무 빠르게 반복하지 않도록 대기

        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.05)


async def video_frame_generator(face_on=True, draw_gesture_on=False):
    global video_frames
    while True:
        try:
            if len(video_frames) > 0:  # 비어있지 않은 경우에만 처리
                frame = video_frames[0]
                if face_on:
                    face_recognition.draw_faces(frame)

                # if draw_gesture_on:
                #     gesture_recognizer.recognize_gesture(frame)
                #     action = gesture_recognizer.this_action
                #     logger.info(f"Recognized action: {action}")  # 인식된 동작 로그
                #     if action != '?':
                #         await gesture_action(action)

                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                await asyncio.sleep(0.1)  # 비어있으면 잠시 대기
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.1)


@app.get("/video_feed/{face_on}/{draw_gesture_on}")
async def get_video_feed(face_on: bool, draw_gesture_on: bool):
    return StreamingResponse(video_frame_generator(face_on, draw_gesture_on),
                             media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/audio_feed")
async def get_audio_feed():
    if not audio_data:
        return {"error": "No audio data available"}

    # WAV 형식으로 변환
    import io
    audio_buffer = io.BytesIO()
    import wave
    with wave.open(audio_buffer, 'wb') as wf:
        wf.setnchannels(1)  # 모노
        wf.setsampwidth(2)  # 16비트 샘플
        wf.setframerate(44100)  # 샘플링 주파수
        wf.writeframes(b''.join(audio_data))  # 오디오 데이터 추가

    audio_buffer.seek(0)  # 버퍼의 시작으로 이동

    return StreamingResponse(audio_buffer, media_type="audio/wav")



# 손동작에 따라 명령 #######################################################################################################
# 마지막 명령 발행 시간 초기화
last_command_time = 0
command_cooldown = 10  # 10초 쿨다운


async def gesture_action(action):
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
########################################################################################################################
