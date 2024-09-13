import imghdr
import mimetypes
import shutil
import tempfile

import logger
import pymysql
import numpy as np
import cv2
from io import BytesIO
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

    faces = {}
    for nickname, photoname in results:
        faces[photoname] = nickname

    return faces

# 파일 이름에서 닉네임을 가져오는 함수
def get_nickname_from_filename(filename):
    faces = get_faces_from_db()
    base_name = os.path.basename(filename)
    name_part = base_name.split('.')[0]
    name_part = name_part.split('(')[0].strip()
    return faces.get(name_part, name_part)

def load_image_from_blob(blob_data):
    try:
        if not blob_data:
            print("No data in blob.")
            return None

        # Check if the blob_data is a valid image format
        with BytesIO(blob_data) as buf:
            buf.seek(0)
            image = Image.open(buf)
            image = image.convert('RGB')  # Ensure RGB format
            return np.array(image)
    except Exception as e:
        print(f"Error loading image from blob: {e}")
        return None

def fetch_family_photos():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get family relationships
    query = """
        SELECT user1.photoname, user2.photoname 
        FROM familyship 
        JOIN userentity user1 ON familyship.user1_id = user1.id
        JOIN userentity user2 ON familyship.user2_id = user2.id
        WHERE user1.photoname IS NOT NULL AND user2.photoname IS NOT NULL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create a dictionary to store family photos
    family_photos = {}

    for photo1, photo2 in results:
        if photo1:
            family_photos[photo1] = 'family_member'
        if photo2:
            family_photos[photo2] = 'family_member'

    # Save photos to temporary files
    temp_dir = tempfile.mkdtemp()

    for photo_path in family_photos.keys():
        # If photo_path is a bytes object, try to identify it as an image
        if isinstance(photo_path, bytes):
            image_type = imghdr.what(None, h=photo_path)  # Detect image type from binary data
            if image_type:
                # If valid image, save it to a temporary file
                temp_file_path = os.path.join(temp_dir, f"image_{os.urandom(4).hex()}.{image_type}")
                with open(temp_file_path, 'wb') as f:
                    f.write(photo_path)
            else:
                print(f"Unknown binary data, skipping: {photo_path}")
        else:
            # Assuming the path is already a string and valid file path
            temp_file_path = os.path.join(temp_dir, os.path.basename(photo_path))
            shutil.copy(photo_path, temp_file_path)

    return temp_dir