
from fastapi import FastAPI
import pymysql
import os
from dotenv import load_dotenv

app = FastAPI()

# .env 파일에서 환경 변수 로드
load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def schedule_date(date):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT user_name, task, time
            FROM schedules
            WHERE date = %s
            ORDER BY time
            """
            cursor.execute(query, (date,))
            result = cursor.fetchall()
            return [{"user_name": row[0], "task": row[1], "time": str(row[2])} for row in result]
    finally:
        connection.close()
# url에 날짜를 줘서 날짜별로 일정 확인 http://localhost:8000/calendar?date=2024-07-30
# 반환 형식:
# {
#     "date": "2024-07-30",
#     "schedules": [
#         {
#             "user_name": "맹구",
#             "task": "돌 줍기",
#             "time": "10:00:00"
#         }
#     ]
# }

@app.get("/calendar")
def calendar(date: str):
    schedules = schedule_date(date)
    return {"date": date, "schedules": schedules}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)