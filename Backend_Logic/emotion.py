import tensorflow as tf
import numpy as np
import cv2

# 감정 분석 모델 로드
model = tf.keras.models.load_model('emotion_detection_model.h5')

emotion_dict = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

def preprocess_face_image(image):
    target_size = (48, 48)
    image_resized = cv2.resize(image, target_size)

    # 이미지가 그레이스케일인지 확인
    if len(image_resized.shape) == 2 or image_resized.shape[2] == 1:
        image_equalized = cv2.equalizeHist(image_resized)
        image_resized = cv2.cvtColor(image_equalized, cv2.COLOR_GRAY2RGB)
    else:
        gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        image_resized = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)

    image_normalized = cv2.normalize(image_resized, None, 0, 255, cv2.NORM_MINMAX)
    image_filtered = cv2.GaussianBlur(image_normalized, (3, 3), 0)

    # 최종적으로 이미지가 3채널(RGB)인지 확인
    if len(image_filtered.shape) == 2 or image_filtered.shape[2] == 1:
        image_filtered = cv2.cvtColor(image_filtered, cv2.COLOR_GRAY2RGB)

    return image_filtered


def predict_emotion(image):
    # 이미지 전처리 및 감정 예측 코드
    # 모델을 이용하여 감정을 예측
    processed_image = preprocess_face_image(image)  # 필요한 경우 전처리
    predictions = model.predict(np.expand_dims(processed_image, axis=0))
    emotion = np.argmax(predictions)
    return emotion
