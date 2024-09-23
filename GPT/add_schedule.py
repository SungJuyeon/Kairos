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


def add_schedule(user_name, date, time, task):
    try:
        # MySQL 데이터베이스 연결
        conn = pymysql.connect(
            host=db_host,  # 호스트 주소
            user=db_user,  # MySQL 사용자 이름
            password=db_password,  # MySQL 비밀번호
            database=db_name,  # 사용할 데이터베이스 이름
            charset='utf8'
        )

        # 커서 생성
        cursor = conn.cursor()

        # SQL 쿼리 작성
        query = """
            INSERT INTO schedules (user_name, date, time, task)
            VALUES (%s, %s, %s, %s)
        """
        values = (user_name, date, time, task)

        # 쿼리 실행
        cursor.execute(query, values)
        conn.commit()

        return f"{user_name}의 일정에 '{task}'가 {date} {time}에 추가되었습니다."

    except pymysql.MySQLError as e:
        # 오류 발생 시 메시지 출력
        return f"일정 추가 오류: {e}"

    finally:
        # 커서 및 연결 종료
        cursor.close()
        conn.close()
