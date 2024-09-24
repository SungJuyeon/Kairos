import pymysql
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

def select_schedule(user_name, date):
    # MySQL 데이터베이스 연결
    conn = pymysql.connect(
        host=db_host,       # 호스트 주소
        user=db_user,       # MySQL 사용자 이름
        password=db_password, # MySQL 비밀번호
        database=db_name,   # 사용할 데이터베이스 이름
        charset='utf8'
    )
    #커서는 데이터베이스에 SQL문을 실행하거나 실행된 결과를 돌려받는 통로
    cursor = conn.cursor()

    # 일정 조회
    query = 'SELECT time, task FROM schedules WHERE user_name = %s AND date = %s'
    values = (user_name, date)
    cursor.execute(query, values)
    schedules = cursor.fetchall()

    conn.close()
    return schedules