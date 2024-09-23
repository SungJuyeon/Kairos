import pymysql
import os
import logging
from dotenv import load_dotenv

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
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

def fetch_user_id_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM userentity WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]
    return None

def fetch_family_photos(username):
    user_id = fetch_user_id_by_username(username)
    if user_id is None:
        logging.error(f"User with username {username} not found.")
        return

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

    for photo1, nickname1, photo2, nickname2 in results:
        if nickname1:
            family_nicknames.add(nickname1)
            if photo1:
                photo1_path = os.path.join(faces_dir, f"{nickname1}.jpg")
                with open(photo1_path, 'wb') as f:
                    f.write(photo1)

        if nickname2:
            family_nicknames.add(nickname2)
            if photo2:
                photo2_path = os.path.join(faces_dir, f"{nickname2}.jpg")
                with open(photo2_path, 'wb') as f:
                    f.write(photo2)

    logging.info(f"가족 nicknames: {', '.join(family_nicknames)}")


async def current_userId(token: str):
    try:
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('username')

        if not user_id:
            raise ValueError("User ID not found in token")
        return user_id
    except jwt.JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
