import cv2
import asyncio
import logging

generate_frames_task = None
#generate_frames 함수를 비동기작업 시작하는 함수
async def start_generate_frames(client):
    global generate_frames_task
    generate_frames_task = asyncio.create_task(generate_frames(client))

#비동기 작업중인 generate_frames 함수를 종료하는 함수
async def stop_generate_frames():
    global generate_frames_task
    generate_frames_task.cancel()
    generate_frames_task = None

    
    
# 영상 전송 ####################################################################
async def generate_frames(client):
    cap = cv2.VideoCapture(0)  # 카메라 초기화
    if not cap.isOpened():
        logging.error("카메라를 열 수 없습니다.")
        return
    try:
        while True:
                ret, frame = cap.read()
                if not ret:
                    logging.warning("Failed to capture frame")
                    await asyncio.sleep(1)  # 프레임 캡처 실패 시 대기
                    continue

                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                from robot_controller import MQTT_TOPIC_VIDEO
                client.publish(MQTT_TOPIC_VIDEO, frame_data)  # 비디오 프레임 전송
                # logging.info("Sent a video frame")

                await asyncio.sleep(0.05)  # 전송 주기 조정
    except Exception as e:
        logging.error(f"Error in generate_frames: {e}")
        await asyncio.sleep(1)  # 오류 발생 시 대기
    finally:
        cap.release()  # 카메라 자원 해제