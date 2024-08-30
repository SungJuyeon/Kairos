import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# 데이터셋 로드
df = pd.read_csv('fer2013.csv')

# 픽셀 데이터를 numpy array로 변환
df['pixels'] = df['pixels'].apply(lambda pixel: np.fromstring(pixel, sep=' '))
df.head()

# 이미지 크기 및 채널 수 설정
img_size = 48
channels = 1

# 이미지 배열로 변환하고 정규화
X = np.array(df['pixels'].tolist())
X = X.reshape(-1, img_size, img_size, channels)
X = X / 255.0

# 감정 레이블을 One-Hot 인코딩
encoder = OneHotEncoder()
y = encoder.fit_transform(df['emotion'].values.reshape(-1, 1)).toarray()

# 데이터셋을 학습용과 테스트용으로 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 정의 (Functional API 사용)
inputs = tf.keras.Input(shape=(img_size, img_size, channels))
x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu')(inputs)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)
x = tf.keras.layers.Dropout(0.25)(x)
x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
x = tf.keras.layers.MaxPooling2D((2, 2))(x)
x = tf.keras.layers.Dropout(0.25)(x)
x = tf.keras.layers.Flatten()(x)
x = tf.keras.layers.Dense(128, activation='relu')(x)
x = tf.keras.layers.Dropout(0.5)(x)
outputs = tf.keras.layers.Dense(y.shape[1], activation='softmax')(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

# 모델 컴파일
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 모델 학습
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=30, batch_size=64)

# 학습된 모델 저장
model.save('emotion_detection_model.h5')
