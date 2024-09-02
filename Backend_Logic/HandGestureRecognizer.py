import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model

class HandGestureRecognizer:
    def __init__(self, model_path):
        self.actions = ['come', 'away', 'spin']
        self.seq_length = 30
        self.model = load_model(model_path)

        # MediaPipe hands model
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        self.seq = []
        self.action_seq = []
        self.last_action = None
        self.this_action = '?'

    def recognize_gesture(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.hands.process(img_rgb)

        if result.multi_hand_landmarks is not None:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=4),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5)
                )

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
                self.seq.append(d)

                if len(self.seq) < self.seq_length:
                    continue

                input_data = np.expand_dims(np.array(self.seq[-self.seq_length:], dtype=np.float32), axis=0)
                y_pred = self.model.predict(input_data).squeeze()

                i_pred = int(np.argmax(y_pred))
                conf = y_pred[i_pred]

                if conf < 0.9:
                    continue

                action = self.actions[i_pred]
                self.action_seq.append(action)

                if len(self.action_seq) < 5:  # 기준 5번 연속
                    continue

                this_action = '?'
                if self.action_seq[-1] == self.action_seq[-2] == self.action_seq[-3] == self.action_seq[-4] == self.action_seq[-5]:
                    this_action = action

                cv2.putText(img, f'{this_action.upper()}', org=(int(hand_landmarks.landmark[0].x * img.shape[1]),
                                                                int(hand_landmarks.landmark[0].y * img.shape[0] + 20)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, color=(0, 255, 0), thickness=2)

        return img