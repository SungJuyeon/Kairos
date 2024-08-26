# import cv2
# import numpy as np
# from scipy.spatial.distance import cosine
# import os
# from werkzeug.utils import secure_filename
# from flask import Flask, jsonify, send_from_directory, request
#
# # 등록된 얼굴 데이터베이스
# registered_faces = {}
#
# # 얼굴 등록 함수
# def register_face(image, name):
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(48, 48), flags=cv2.CASCADE_SCALE_IMAGE)
#
#     if len(detected_faces) > 0:
#         (x, y, w, h) = detected_faces[0]
#         face = gray[y:y+h, x:x+w]
#         face = cv2.resize(face, (48, 48))
#         filename = f"{secure_filename(name)}.jpg"
#         registered_faces[name] = face
#
#         # 얼굴 이미지 저장
#         if not os.path.exists("registered_faces"):
#             os.makedirs("registered_faces")
#         cv2.imwrite(os.path.join("registered_faces", filename), face)
#
#         return True
#     return False
#
# # 얼굴 비교 함수
# def compare_faces(face1, face2):
#     return cosine(face1.flatten(), face2.flatten())
#
# # 얼굴 인식 함수
# def recognize_face(detected_face):
#     min_distance = float('inf')
#     recognized_name = None
#     for name, registered_face in registered_faces.items():
#         distance = compare_faces(detected_face, registered_face)
#         if distance < min_distance and distance < 0.4:  # 코사인 유사도 기준
#             min_distance = distance
#             recognized_name = name
#     return recognized_name
#
# # 등록된 얼굴 정보 조회 함수
# def get_registered_faces_info():
#     faces_info = []
#
#     for name, face in registered_faces.items():
#         filename = f"{secure_filename(name)}.jpg"
#         face_image_path = f"/face_images/{filename}"
#
#         # 얼굴 이미지 저장
#         face_image_path_full = os.path.join("registered_faces", filename)
#
#         try:
#             # 얼굴 이미지 저장 시도
#             saved = cv2.imwrite(face_image_path_full, face)
#
#             if not saved:
#                 print(f"Error saving face image for {name} at {face_image_path_full}")
#                 continue  # 이미지 저장 실패 시 다음으로 넘어감
#
#         except Exception as e:
#             print(f"Exception occurred while saving face image for {name}: {e}")
#             continue  # 예외 발생 시 다음으로 넘어감
#
#         # 얼굴 정보 추가
#         faces_info.append({
#             'name': name,
#             'image_path': face_image_path
#         })
#
#     return faces_info
#
#
# # Flask 애플리케이션
# app = Flask(__name__)
#
# # 등록된 얼굴 정보 조회 라우트
# @app.route('/registered_faces', methods=['GET'])
# def get_registered_faces():
#     faces_info = get_registered_faces_info()
#     return jsonify(faces_info)
#
# # 얼굴 이미지 파일 제공 라우트
# @app.route('/face_images/<filename>', methods=['GET'])
# def get_face_image(filename):
#     return send_from_directory('registered_faces', filename)
#
# # 얼굴 등록 라우트
# @app.route('/register_face', methods=['POST'])
# def register_face_route():
#     if 'file' not in request.files or 'name' not in request.form:
#         return jsonify({'error': 'No file or name'}), 400
#
#     file = request.files['file']
#     name = request.form['name']
#
#     if file and name:
#         # 이미지 읽기
#         image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
#
#         # 얼굴 등록
#         if register_face(image, name):
#             # 파일 이름과 경로 설정
#             filename = f"{secure_filename(name)}.jpg"
#             face_image_path = f"/face_images/{filename}"
#
#             return jsonify({
#                 'status': 'Face registered successfully',
#                 'name': name,
#                 'image_path': face_image_path
#             }), 200
#         else:
#             return jsonify({'error': 'Face registration failed'}), 400
#     else:
#         return jsonify({'error': 'Invalid file or name'}), 400
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080, debug=True)