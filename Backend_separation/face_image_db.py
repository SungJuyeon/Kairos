import logger
import pymysql
import numpy as np
import cv2
from PIL import Image
import io
import os
from dotenv import load_dotenv
import logging

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

def get_all_user_ids():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT id FROM userentity"
            cursor.execute(query)
            # 모든 사용자 ID 가져오기
            user_ids = [row[0] for row in cursor.fetchall()]
    finally:
        connection.close()

    return user_ids

def get_nickname_from_user_id(user_id):
    """ID에 해당하는 닉네임"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT nickname FROM userentity WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
    finally:
        connection.close()

    return result[0] if result else "unknown"

def get_face_image_from_blob(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Query to get the BLOB data for the given user_id
            sql = "SELECT photoname FROM userentity WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if result:
                # Get the BLOB data
                blob_data = result[0]
                if blob_data:
                    # Convert BLOB to numpy array
                    image_np = np.frombuffer(blob_data, np.uint8)
                    # Decode numpy array to image
                    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
                    if image is not None:
                        nickname = get_nickname_from_user_id(user_id)
                        logging.info(f"Successfully loaded image for nickname: {nickname}")
                        return image, nickname
                    else:
                        logging.error("Failed to decode image from BLOB data.")
                        return None, None
                else:
                    logging.error("BLOB data is empty.")
                    return None, None
            else:
                logging.error("No image found for the given user_id.")
                return None, None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None, None
    finally:
        connection.close()


def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

###face_recog_db_test.py에서 사용
def get_faces_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT nickname, photoname FROM userentity WHERE photoname IS NOT NULL"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    faces = []
    for nickname, photoname in results:
        faces.append((nickname, photoname))

    return faces
