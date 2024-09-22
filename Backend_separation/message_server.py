import os
import json
import pymysql
from fastapi import FastAPI, WebSocket, HTTPException
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
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
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
    return result['id'] if result else None

# 사용자 이름을 user_id로부터 가져오기
def fetch_username_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT username FROM userentity WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result['username'] if result else None

# 가족 목록 가져오기
def get_family(user_id):
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
    family_members = [row['id'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return family_members

# 메시지 저장 함수
def log_message(sender_id, message):
    family_members = get_family(sender_id)
    all_recipients = family_members + [sender_id]
    for recipient_id in all_recipients:
        message_log = f"{recipient_id}_messages.json"
        messages = []
        if os.path.exists(message_log):
            with open(message_log, 'r', encoding='utf-8') as file:
                try:
                    messages = json.load(file)
                except json.JSONDecodeError:
                    messages = []
        messages.append({"sender_id": sender_id, "message": message})
        with open(message_log, 'w', encoding='utf-8') as file:
            json.dump(messages, file, indent=4, ensure_ascii=False)

# JWT에서 username 추출 함수
def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("username")
    except jwt.JWTError:
        return None

# WebSocket 핸들러
async def handle_connection(websocket: WebSocket):
    global client_sockets
    await websocket.accept()
    user_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if "token" in message_data:
                token = message_data["token"]
                username = get_username_from_token(token)
                if username is None:
                    continue
                user_id = fetch_user_id_by_username(username)
                if user_id is not None:
                    if not any(client[0] == websocket for client in client_sockets):
                        client_sockets.append((websocket, user_id))

            if "message" in message_data and user_id is not None:
                message = message_data["message"]
                log_message(user_id, message)
                current_user_family = get_family(user_id)

                for client, client_user_id in client_sockets:
                    if client_user_id == user_id or client_user_id in current_user_family:
                        await client.send_text(f"{user_id}: {message}")

    except Exception:
        pass
    finally:
        if user_id is not None:
            client_sockets = [c for c in client_sockets if c[1] != user_id]

# WebSocket 라우트
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await handle_connection(websocket)

# HTTP 라우트 - 채팅 페이지
@app.get("/chat", response_class=HTMLResponse)
async def read_chat():
    return templates.TemplateResponse("chat.html", {"request": {}})

@app.get("/messages/{username}")
async def get_messages(username: str):
    # 입력된 username에 해당하는 사용자 ID를 가져옴
    user_id = fetch_user_id_by_username(username)
    print(f">> User ID for {username}: {user_id}")  # 사용자 ID 확인

    if user_id is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 사용자 자신의 메시지 파일만 로드
    message_log = f"{user_id}_messages.json"
    print(f">> Checking for messages in: {message_log}")  # 파일 경로 확인

    if not os.path.exists(message_log):
        print(f">> File does not exist: {message_log}")  # 파일 존재 확인
        return {"messages": []}

    # 메시지 파일을 읽어옴
    with open(message_log, "r", encoding="utf-8") as file:
        try:
            messages = json.load(file)
            print(f">> Messages loaded for {username}: {messages}")  # 메시지 로드 확인
        except json.JSONDecodeError:
            messages = []
            print(f">> JSONDecodeError while loading messages for {username}.")

    # 사용자 본인의 메시지만 반환
    return {"messages": messages}  # 사용자 메시지 반환

# 서버 실행
if __name__ == "__main__":
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
