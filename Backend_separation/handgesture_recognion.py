import cv2
import numpy as np
import mediapipe as mp
from tensorflow import keras
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

actions = ['come', 'away', 'spin']
seq_length = 30
model = keras.models.load_model('model.keras')

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

seq = []
action_seq = []
last_action = None
this_action = '?'

def detect_gesture(frame):
    global seq, action_seq, last_action, this_action

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks is not None:
        for hand_landmarks in result.multi_hand_landmarks:
            joint = np.zeros((21, 4))
            for j, lm in enumerate(hand_landmarks.landmark):
                joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

            v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :3]
            v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :3]
            v = v2 - v1
            v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

            angle = np.arccos(np.einsum('nt,nt->n',
                                        v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
                                        v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))
            angle = np.degrees(angle)

            d = np.concatenate([joint.flatten(), angle])
            seq.append(d)

            if len(seq) < seq_length:
                continue

            input_data = np.expand_dims(np.array(seq[-seq_length:], dtype=np.float32), axis=0)
            y_pred = model.predict(input_data).squeeze()

            i_pred = int(np.argmax(y_pred))
            conf = y_pred[i_pred]

            if conf < 0.9:
                continue

            action = actions[i_pred]
            action_seq.append(action)

            if len(action_seq) < 5:
                continue

            this_action = '?'
            if action_seq[-1] == action_seq[-2] == action_seq[-3] == action_seq[-4] == action_seq[-5]:
                this_action = action

            if this_action != last_action:
                last_action = this_action
                logger.info(f"Detected gesture: {this_action}")

    return this_action, result.multi_hand_landmarks

def draw_gesture(frame, multi_hand_landmarks, action):
    if multi_hand_landmarks:
        for hand_landmarks in multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=4),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5)
            )

    cv2.putText(frame, f'Gesture: {action.upper()}', 
                org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                fontScale=1, 
                color=(0, 255, 0), 
                thickness=2)

    return frame

async def recognize_gesture_periodically(video_frames):
    logger.info("손동작 인식 업데이트 시작")
    while True:
        try:
            if video_frames:
                frame = video_frames[-1]
                action, _ = detect_gesture(frame)
                logger.info(f"현재 감지된 동작: {action}")
            await asyncio.sleep(0.1)
        except IndexError:
            logger.info("비디오 프레임 리스트가 비어 있습니다.")
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"손동작 인식 중 오류 발생: {e}")
            await asyncio.sleep(0.1)
