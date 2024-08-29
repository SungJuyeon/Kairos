# 손동작 인식
action = gesture_recognizer.recognize_gesture(img_encode)
logger.info(f"Recognized action: {action}")  # 인식된 동작 로그

if action != '?':
    await gesture_action(action)  # 동작에 따라 명령을 발행

await video_frames_queue.put(img_encode)  # 인식된 프레임을 큐에 추가
return





# 얼굴 인식 비디오 스트림 엔드포인트 추가
frame_interval = 7  # 5 프레임마다 처리
frame_counter = 0

async def face_video_frame_generator():
    global frame_counter
    while True:
        try:
            frame = await video_frames_queue.get()

            faces = face_recognition.detect_faces(frame)

            if frame_counter % frame_interval == 0:
                face_recognition.recognize_faces(frame, faces)

            face_recognition.draw_faces(frame, faces)
            frame_counter += 1

            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await asyncio.sleep(0.1)







async def video_frame_generator():
    while True:
        try:
            img = await video_frames_queue.get()
            _, jpeg = cv2.imencode('.jpg', img)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            video_frames_queue.task_done()  # 작업 완료 표시
        except Exception as e:
            logger.error(f"Error while sending video frame: {e}")
            await asyncio.sleep(0.1)


@app.get("/video_feed/{run_face_recognition}/{run_another_logic}")
async def get_video_feed(run_face_recognition: bool = True, run_another_logic: bool = True):
    return StreamingResponse(video_frame_generator(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.post("/set_hand_gesture/{state}")
async def set_hand_gesture(state: str):
    global hand_gesture
    if state.lower() == "on":
        hand_gesture = True
        return {"message": "Hand gesture mode enabled"}
    elif state.lower() == "off":
        hand_gesture = False
        return {"message": "Hand gesture mode disabled"}
    else:
        return {"error": "Invalid state"}, 400


async def voice_data_generator():
    while True:
        if voice_data:
            yield voice_data.encode('utf-8')
        await asyncio.sleep(0.1)


@app.get("/get_voice_data")
async def get_voice_data():
    return StreamingResponse(voice_data_generator(), media_type="application/octet-stream")
