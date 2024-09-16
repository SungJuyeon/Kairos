import pymysql
import os
from dotenv import load_dotenv
import logging
from fastapi import Request, HTTPException, Depends
import jwt  # PyJWT 라이브러리 필요
from jwt import PyJWKClient

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

SECRET_KEY = os.getenv('SECRET_KEY')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def fetch_family_photos(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT user1.photoname, user1.nickname, user2.photoname, user2.nickname 
        FROM familyship 
        JOIN userentity user1 ON familyship.user1_id = user1.id
        JOIN userentity user2 ON familyship.user2_id = user2.id
        WHERE (user1.id = %s OR user2.id = %s) AND user1.photoname IS NOT NULL AND user2.photoname IS NOT NULL
    """
    cursor.execute(query, (user_id, user_id))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # 'faces' 디렉토리에 사진 저장
    faces_dir = 'faces'
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)

    family_nicknames = set()

    for idx, (photo1, nickname1, photo2, nickname2) in enumerate(results):
        family_nicknames.update([nickname1, nickname2])

        if photo1:
            photo1_path = os.path.join(faces_dir, f"{nickname1}.jpg")
            with open(photo1_path, 'wb') as f:
                f.write(photo1)

        if photo2:
            photo2_path = os.path.join(faces_dir, f"{nickname2}.jpg")
            with open(photo2_path, 'wb') as f:
                f.write(photo2)

    logging.info(f"가족 nicknames: {', '.join(family_nicknames)}")


async def current_userId(token: str):
    try:
        # JWT 토큰 디코딩
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")  # 토큰에서 user_id 가져오기
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
