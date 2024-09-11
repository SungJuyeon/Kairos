# import os
# import json
# from datetime import datetime
#
# def get_emotion_file():
#     base_dir = "../Backend_Logic/emotions"
#     today = datetime.today().strftime('%Y%m%d')
#     return os.path.join(base_dir, f"{today}.json")
#
# print("Expected file path:", get_emotion_file())
# print("File exists:", os.path.exists(get_emotion_file()))
#
# # 감정 결과 저장 함수
# def save_emotion_result(emotion):
#     file_path = get_emotion_file()
#
#     # 기존 데이터 로드
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as file:
#             emotion_data = json.load(file)
#     else:
#         emotion_data = {emotion: 0 for emotion in ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']}
#
#     # 감정 카운트 증가
#     if emotion in emotion_data:
#         emotion_data[emotion] += 1
#
#     # 데이터 저장
#     with open(file_path, 'w') as file:
#         json.dump(emotion_data, file)
#
# # 감정 순위 반환 함수
# def get_emotion_ranking():
#     file_path = get_emotion_file()
#
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as file:
#             emotion_data = json.load(file)
#         # 감정을 빈도에 따라 내림차순으로 정렬
#         sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
#         return sorted_emotions
#     else:
#         return []
#
# def get_most_frequent_emotion():
#     file_path = get_emotion_file()
#
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as file:
#             emotion_data = json.load(file)
#
#         if emotion_data and any(emotion_data.values()):  # Check if there are any non-zero values
#             # 가장 높은 빈도를 가진 감정을 찾기
#             most_frequent_emotion = max(emotion_data.items(), key=lambda x: x[1])
#             return most_frequent_emotion
#         else:
#             return ("No emotion data available", 0)
#     else:
#         return ("No emotion data available", 0)
