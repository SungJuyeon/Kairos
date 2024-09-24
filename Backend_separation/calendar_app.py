import pymysql
from pydantic import BaseModel
from typing import Dict, List
from fastapi import HTTPException, Header
import os
import jwt
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# JWT 비밀 키 로드
SECRET_KEY = os.getenv('SECRET_KEY')

# Schedule 데이터 모델
class Schedule(BaseModel):
    user_name: str
    task: str
    date: str
    time: str

# DB 연결 함수
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# JWT 토큰에서 사용자 이름 추출
def get_username_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("username")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
# 사용자 ID를 username으로부터 가져오기
def fetch_user_id_by_username(username: str):
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

# 가족 관계에 있는 사용자 이름 목록 가져오기
def get_family_members(user_id: int) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT u.username FROM familyship f
    JOIN userentity u ON (u.id = f.user2_id OR u.id = f.user1_id)
    WHERE (f.user1_id = %s OR f.user2_id = %s) AND u.id != %s
    """
    cursor.execute(query, (user_id, user_id, user_id))
    family_members = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return family_members

def get_all_schedules(token: str) -> Dict[str, List[Dict]]:
    username = get_username_from_token(token)
    user_id = fetch_user_id_by_username(username)

    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    family_members = get_family_members(user_id)
    family_members.append(username)  # 자신의 username도 포함

    # family_members의 각 ID에 대해 username을 가져옴
    family_members_usernames = []
    for member_id in family_members:
        # member_id는 int여야 함
        fetched_username = fetch_username_by_id(int(member_id))  # int로 변환
        family_members_usernames.append(fetched_username)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # family_members와 일치하는 user_name만 선택
            placeholders = ', '.join(['%s'] * len(family_members_usernames))  # %s 플레이스홀더 생성
            query = f"""
            SELECT id, date, user_name, task, time
            FROM schedules
            WHERE user_name IN ({placeholders})
            ORDER BY date, time
            """
            cursor.execute(query, family_members_usernames)  # 리스트로 전달
            result = cursor.fetchall()

            schedules_by_date = {}
            for row in result:
                date = row[1].strftime('%Y-%m-%d')
                if date not in schedules_by_date:
                    schedules_by_date[date] = []
                schedules_by_date[date].append({
                    "id": row[0],  # 일정 ID
                    "date": date,
                    "user_name": row[2],
                    "task": row[3],
                    "time": str(row[4])
                })
            return schedules_by_date
    finally:
        connection.close()


def fetch_username_by_id(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT username FROM userentity WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result[0] if result else None



def add_schedules(schedule: Schedule, token: str) -> Dict[str, str]:
    username = get_username_from_token(token)
    user_id = fetch_user_id_by_username(username)

    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO schedules (date, user_name, task, time)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (schedule.date, schedule.user_name, schedule.task, schedule.time))
            connection.commit()
            return {"message": "Schedule added successfully"}
    finally:
        connection.close()



def delete_schedule(schedule_id: int, token: str) -> Dict[str, str]:
    username = get_username_from_token(token)
    user_id = fetch_user_id_by_username(username)

    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    family_members = get_family_members(user_id)
    family_members.append(username)  # 자신의 username 포함

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 해당 일정이 가족 관계 사용자의 일정인지 확인
            query = """
            SELECT user_name FROM schedules WHERE id = %s
            """
            cursor.execute(query, (schedule_id,))
            result = cursor.fetchone()

            if result is None or result[0] not in family_members:
                raise HTTPException(status_code=403, detail="Not authorized to delete this schedule")

            # 일정 삭제
            query = "DELETE FROM schedules WHERE id = %s"
            cursor.execute(query, (schedule_id,))
            connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Schedule not found")
            return {"message": f"일정(ID: {schedule_id})이 성공적으로 삭제되었습니다."}
    finally:
        connection.close()