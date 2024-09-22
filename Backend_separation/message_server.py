import os
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
message_log = "message.json"
client_sockets = []  # 연결된 클라이언트 목록

# 메시지 저장 함수
def log_message(addr, message):
    if not os.path.exists(message_log):
        with open(message_log, 'w') as file:
            json.dump([], file)

    with open(message_log, 'r') as file:
        messages = json.load(file)

    messages.append({"address": addr, "message": message})

    with open(message_log, 'w') as file:
        json.dump(messages, file, indent=4)

# WebSocket 핸들러
async def handle_connection(websocket: WebSocket):
    await websocket.accept()
    client_sockets.append(websocket)
    print(f'>> New connection from {websocket.client.host}:{websocket.client.port}')

    try:
        while True:
            message = await websocket.receive_text()  # 메시지 수신
            addr = f"{websocket.client.host}:{websocket.client.port}"
            print(f'>> Received from {addr}: {message}')
            log_message(addr, message)

            # 모든 클라이언트에게 메시지 브로드캐스트
            for client in client_sockets:
                if client != websocket:
                    await client.send_text(f"Broadcast: {message}")
    except Exception as e:
        print(f'>> Connection closed: {e}')
    finally:
        client_sockets.remove(websocket)

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