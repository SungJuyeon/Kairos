 import os
import shutil
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import base64
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def clear_faces_directory(faces_dir):
    if os.path.exists(faces_dir):
        shutil.rmtree(faces_dir)
    os.makedirs(faces_dir)
    logger.info(f"faces 디렉토리를 비우고 새로 생성했습니다: {faces_dir}")

def load_faces_from_db():
    try:
        # faces 디렉토리 생성 및 초기화
        faces_dir = os.path.join(os.path.dirname(__file__), 'faces')
        clear_faces_directory(faces_dir)
        
        # 데이터베이스 연결
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 사용자 정보 조회
            query = "SELECT nickname, photoname FROM userentity"
            cursor.execute(query)
            records = cursor.fetchall()
            
            for record in records:
                nickname, photoname = record
                if photoname:
                    try:
                        # 이미지 데이터 형식 확인
                        #logger.info(f"사용자 {nickname}의 이미지 데이터 형식: {type(photoname)}")
                        #logger.info(f"이미지 데이터 시작 부분: {photoname[:50]}")  # 처음 50자만 출력
                        
                        # Base64 문자열에서 'data:image/jpeg;base64,' 부분 제거
                        if isinstance(photoname, str) and photoname.startswith('data:image/jpeg;base64,'):
                            photoname = photoname.split(',', 1)[1]
                        
                        # 패딩 추가 (필요한 경우)
                        if isinstance(photoname, str):
                            photoname += '=' * ((4 - len(photoname) % 4) % 4)
                        
                        # BLOB 데이터를 이미지 파일로 저장
                        if isinstance(photoname, str):
                            image_data = base64.b64decode(photoname)
                        else:
                            image_data = photoname  # 이미 바이너리 데이터인 경우
                        
                        file_path = os.path.join(faces_dir, f"{nickname}.jpg")
                        with open(file_path, 'wb') as file:
                            file.write(image_data)
                        #logger.info(f"저장된 이미지: {file_path}")
                    except Exception as e:
                        logger.error(f"사용자 {nickname}의 사진 처리 중 오류 발생: {e}")
                else:
                    logger.warning(f"사용자 {nickname}의 사진이 없습니다.")
            
            logger.info("모든 얼굴 이미지가 성공적으로 로드되었습니다.")
    
    except Error as e:
        logger.error(f"데이터베이스 오류: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("데이터베이스 연결이 종료되었습니다.")

if __name__ == "__main__":
    load_faces_from_db()