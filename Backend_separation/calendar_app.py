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

def get_all_schedules():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT date, user_name, task, time
            FROM schedules
            ORDER BY date, time
            """
            cursor.execute(query)
            result = cursor.fetchall()

            schedules_by_date = {}
            for row in result:
                date = row[0].strftime('%Y-%m-%d')
                if date not in schedules_by_date:
                    schedules_by_date[date] = []
                schedules_by_date[date].append({
                    "user_name": row[1],
                    "task": row[2],
                    "time": str(row[3])
                })
            return schedules_by_date
    finally:
        connection.close()

#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)