import logging
import os
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf 
import asyncio
from gesture_action import gesture_action
from video_processing import video_frames
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.models import Model

# 전역 변수
actions = ['come', 'away', 'spin']
seq_length = 30
model = None
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = None
seq = []
action_seq = []
last_action = None
this_action = '?'
hand_landmarks = None
hand_gesture_action = '?'
hand_gesture_landmarks = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_model():
    input_layer = Input(shape=(30, 99))
    x = LSTM(64)(input_layer)
    x = Dense(32, activation='relu')(x)
    output = Dense(3, activation='softmax')(x)
    return Model(inputs=input_layer, outputs=output)

def init():
    global model, hands
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "models", "model.keras")
    try:
        if os.path.exists(model_path):
            logger.info(f"모델 파일 경로: {model_path}")
            
            # 새 모델 생성
            new_model = create_model()
            
            # 가중치만 로드
            new_model.load_weights(model_path)
            
            model = new_model
            logger.info("모델 가중치를 성공적으로 로드했습니다.")
            
            # 모델 구조 출력
            model.summary()
            
            # 모델 컴파일
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            logger.info("모델 컴파일 완료")
        else:
            logger.error(f"모델 파일을 찾을 수 없습니다: {model_path}")
            return False
    except Exception as e:
        logger.error(f"모델 로딩 중 오류 발생: {str(e)}")
        logger.exception("상세 오류:")
        return False

    # MediaPipe Hands 초기화
    try:
        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        logger.info("MediaPipe Hands 초기화 완료")
    except Exception as e:
        logger.error(f"MediaPipe Hands 초기화 중 오류 발생: {str(e)}")
        logger.exception("상세 오류:")
        return False
    
    return True

def recognize_and_store_gesture(img):
    global seq, action_seq, this_action, hand_landmarks
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks is not None:
        for hand_landmarks in result.multi_hand_landmarks:
            joint = np.zeros((21, 4))
            for j, lm in enumerate(hand_landmarks.landmark):
                joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

            # Calculate angles between joints
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

            if len(action_seq) < 5:  # 기준 5번 연속
                continue

            this_action = '?'
            if action_seq[-1] == action_seq[-2] == action_seq[-3] == action_seq[-4] == action_seq[-5]:
                this_action = action

    return this_action, hand_landmarks

def update_hand_gesture(action, landmarks):
    global hand_gesture_action, hand_gesture_landmarks
    hand_gesture_action = action
    hand_gesture_landmarks = landmarks

async def recognize_hand_gesture_periodically():
    global hand_gesture_action, hand_gesture_landmarks
    while True:
        if len(video_frames) > 0 and hands is not None:
            frame = video_frames[-1]
            action, landmarks = recognize_and_store_gesture(frame)
            update_hand_gesture(action, landmarks)
            await gesture_action(action)
        await asyncio.sleep(0.1)  # 0.1초마다 실행

def draw_hand_gesture(image):
    global hand_gesture_action, hand_gesture_landmarks
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        
        hand_gesture_landmarks = results.multi_hand_landmarks[0]
    else:
        hand_gesture_landmarks = None
        hand_gesture_action = '?'
    
    return image, hand_gesture_action, hand_gesture_landmarks





#테스트
def main():
    if init():
        logger.info("초기화 성공")
    else:
        logger.error("초기화 실패")

    video_frames(draw_hand_gesture, hand_gesture_action, hand_gesture_landmarks)

if __name__ == "__main__":
    main()
