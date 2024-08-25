import cv2
import pymysql
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# MySQL 데이터베이스 연결 정보
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# 데이터베이스 연결 함수
def get_db_connection():
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# 얼굴 등록 함수
def register_face_to_db(image, name):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            _, img_encoded = cv2.imencode('.jpg', image)
            img_binary = img_encoded.tobytes()
            sql = "INSERT INTO registered_faces (name, file) VALUES (%s, %s)"
            cursor.execute(sql, (name, img_binary))
            connection.commit()
            return True
    finally:
        connection.close()
    return False

# 등록된 얼굴 정보 조회 함수
def get_registered_faces_from_db():
    connection = get_db_connection()
    faces_info = []
    try:
        with connection.cursor() as cursor:
            # SQL 쿼리 수정: ID 순으로 정렬
            sql = "SELECT id, name, file FROM registered_faces ORDER BY id ASC"
            cursor.execute(sql)
            result = cursor.fetchall()

            for row in result:
                faces_info.append({
                    'id': row['id'],
                    'name': row['name'],
                    'image_data': row['file']
                })
    finally:
        connection.close()
    return faces_info
