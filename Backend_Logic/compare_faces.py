# import cv2
# import numpy as np
# import face_recognition
#
# def preprocess_face_image(image):
#     target_size = (48, 48)
#     image_resized = cv2.resize(image, target_size)
#
#     if len(image_resized.shape) == 2:
#         image_equalized = cv2.equalizeHist(image_resized)
#         image_resized = cv2.cvtColor(image_equalized, cv2.COLOR_GRAY2RGB)
#     else:
#         gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
#         equalized = cv2.equalizeHist(gray)
#         image_resized = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
#
#     image_normalized = cv2.normalize(image_resized, None, 0, 255, cv2.NORM_MINMAX)
#     image_filtered = cv2.GaussianBlur(image_normalized, (3, 3), 0)
#
#     if len(image_filtered.shape) == 2:
#         image_filtered = cv2.cvtColor(image_filtered, cv2.COLOR_GRAY2RGB)
#
#     return image_filtered
#
# def compare_images(image1, image2):
#     # 이미지 크기 조정
#     image1 = cv2.resize(image1, (300, 300))
#     image2 = cv2.resize(image2, (300, 300))
#
#     # 이미지를 그레이스케일로 변환
#     image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
#     image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
#
#     # 히스토그램 계산
#     hist1 = cv2.calcHist([image1_gray], [0], None, [256], [0, 256])
#     hist2 = cv2.calcHist([image2_gray], [0], None, [256], [0, 256])
#
#     # 히스토그램 비교
#     similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
#
#     return similarity
