import os
import json

import messages
import pymysql
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from jose import jwt
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
client_sockets = []

# 환경 변수에서 데이터베이스 연결 정보 가져오기
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set for application")

# 데이터베이스 연결 함수
def get_db_connection():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# 사용자 ID를 username으로부터 가져오기
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

# 가족 목록 가져오기
def get_family(username):
    user_id = fetch_user_id_by_username(username)
    if user_id is None:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT u.id FROM familyship f
    JOIN userentity u ON (u.id = f.user2_id OR u.id = f.user1_id)
    WHERE (f.user1_id = %s OR f.user2_id = %s) AND u.id != %s
    """
    cursor.execute(query, (user_id, user_id, user_id))
    family_members = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return family_members

# 메시지 저장 함수
def log_message(user_id, message):
    message_log = f"{user_id}_messages.json"

    # 메시지를 저장할 리스트 초기화
    messages = []

    # 파일이 존재하지 않으면 새로 생성
    if not os.path.exists(message_log):
        with open(message_log, 'w', encoding='utf-8') as file:
            json.dump(messages, file, indent=4, ensure_ascii=False)

    # 파일이 존재하면 내용을 읽어옴
    with open(message_log, 'r', encoding='utf-8') as file:
        messages = json.load(file)

    messages.append({"message": message})

    with open(message_log, 'w', encoding='utf-8') as file:
        json.dump(messages, file, indent=4, ensure_ascii=False)

# JWT에서 사용자 ID 추출 함수
def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("username")
    except jwt.JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None

# 사용자 ID를 username으로부터 가져오기
def fetch_username_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT username FROM userentity WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result[0]
    return None

# WebSocket 핸들러
async def handle_connection(websocket: WebSocket):
    await websocket.accept()
    print(f'>> New connection from {websocket.client.host}:{websocket.client.port}')

    user_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if "token" in message_data:
                token = message_data["token"]
                username = get_user_id_from_token(token)
                user_id = fetch_user_id_by_username(username)
                if user_id is not None:
                    client_sockets.append((websocket, user_id))
                    print(f'>> User ID: {user_id}')
                else:
                    print(">> Invalid token or user ID could not be retrieved.")

            if "message" in message_data and user_id is not None:
                message = message_data["message"]
                print(f'>> Received from {username}: {message}')
                log_message(username, message)

                # 현재 사용자 가족 목록 가져오기
                current_user_family = get_family(username)

                # 현재 사용자 가족 목록을 한 번만 출력
                print(f'>> {username} family: {current_user_family}')

                # 모든 클라이언트에게 메시지 브로드캐스트 (가족에게만)
                for client, client_user_id in client_sockets:
                    client_family = get_family(fetch_username_by_user_id(client_user_id))
                    print(f'>> user_id: {user_id} current_user_family: {current_user_family}')
                    print(f'>> client_user_id{client_user_id} client_family: {client_family}')
                    # 서로가 가족인지 확인하여 메시지를 전달
                    if user_id in client_family or client_user_id in current_user_family:
                        print(f'>> Sending to {client_user_id}: {user_id}: {message}')
                        await client.send_text(f"{user_id}: {message}")

    except Exception as e:
        print(f'>> Connection closed: {e}')
    finally:
        if user_id is not None:
            client_sockets.remove((websocket, user_id))

# WebSocket 라우트
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await handle_connection(websocket)

# HTTP 라우트
@app.get("/chat", response_class=HTMLResponse)
async def read_chat():
    return templates.TemplateResponse("chat.html", {"request": {}})

# 서버 실행
if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
