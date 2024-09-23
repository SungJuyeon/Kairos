# messages_server.py

import os
import json
import pymysql
from fastapi import WebSocket
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

# 전역 변수 선언
client_sockets = []

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set for application")

def get_db_connection():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
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
        return result['id']
    return None

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

def log_message(sender_id, message):
    family_members = get_family(sender_id)
    all_recipients = family_members + [sender_id]

    for recipient_id in all_recipients:
        message_log = f"{recipient_id}_messages.json"

        if os.path.exists(message_log):
            with open(message_log, 'r', encoding='utf-8') as file:
                try:
                    messages = json.load(file)
                except json.JSONDecodeError:
                    messages = []
        else:
            messages = []

        messages.append({"sender_id": sender_id, "message": message})

        with open(message_log, 'w', encoding='utf-8') as file:
            json.dump(messages, file, indent=4, ensure_ascii=False)

def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        if not username:
            print("Username not found in token.")
            return None
        return username
    except jwt.JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None

async def handle_connection(websocket: WebSocket):
    global client_sockets
    await websocket.accept()
    user_id = None
    print(">> WebSocket 연결 수락됨.")
    try:
        while True:
            data = await websocket.receive_text()
            print(f">> 수신 데이터: {data}")
            try:
                message_data = json.loads(data)
                print(">> JSON 파싱 성공.")
            except json.JSONDecodeError:
                print(">> Invalid JSON data.")
                continue

            if "token" in message_data:
                token = message_data["token"]
                print(">> 토큰 수신:", token)
                username = get_username_from_token(token)
                if username is None:
                    print(">> 토큰에서 username 추출 실패.")
                    continue
                user_id = fetch_user_id_by_username(username)
                if user_id is not None:
                    print(f">> 사용자 ID 추출: {user_id}")
                    if not any(client[0] == websocket for client in client_sockets):
                        client_sockets.append((websocket, user_id))
                        print(f">> 클라이언트 소켓 목록에 추가: {user_id}")
                else:
                    print(">> Invalid token or user ID could not be retrieved.")

            if "message" in message_data and user_id is not None:
                message = message_data["message"]
                print(f">> 메시지 수신 from {user_id}: {message}")
                log_message(user_id, message)

                current_user_family = get_family(user_id)
                print(f">> 가족 목록: {current_user_family}")

                for client, client_user_id in client_sockets:
                    if client_user_id == user_id or client_user_id in current_user_family:
                        try:
                            await client.send_text(f"{user_id}: {message}")
                            print(f">> 메시지 전송 to {client_user_id}: {message}")
                        except Exception as e:
                            print(f">> 메시지 전송 실패 to {client_user_id}: {e}")
    except Exception as e:
        print(f'>> Connection closed: {e}')
    finally:
        if user_id is not None:
            client_sockets = [c for c in client_sockets if c[1] != user_id]
            print(f">> 클라이언트 소켓 목록에서 제거: {user_id}")