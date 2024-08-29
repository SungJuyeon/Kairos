# 손동작 인식
action = gesture_recognizer.recognize_gesture(img_encode)
logger.info(f"Recognized action: {action}")  # 인식된 동작 로그

if action != '?':
    await gesture_action(action)  # 동작에 따라 명령을 발행

await video_frames_queue.put(img_encode)  # 인식된 프레임을 큐에 추가
return









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
