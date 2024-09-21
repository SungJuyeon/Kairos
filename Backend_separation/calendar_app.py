from fastapi import FastAPI, HTTPException
import pymysql
from pydantic import BaseModel
import os
from dotenv import load_dotenv

app = FastAPI()

# .env 파일에서 환경 변수 로드
load_dotenv()

class Schedule(BaseModel):
    user_name: str
    task: str
    date: str
    time: str

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
                    "id": row[0],  # ID 로 delete
                    "user_name": row[1],
                    "task": row[2],
                    "time": str(row[3])
                })
            return schedules_by_date
    finally:
        connection.close()

def add_schedule(schedule: Schedule):
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

def delete_schedule(schedule_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM schedules WHERE id = %s"
            cursor.execute(query, (schedule_id,))
            connection.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Schedule not found")
            return {"message": "Schedule deleted successfully"}
    finally:
        connection.close()

#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)