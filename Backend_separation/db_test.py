# import os
# import httpx
# import asyncio
# from fastapi import FastAPI, Header, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from face_image_db import fetch_family_photos
# from face_recognition import recognize_periodically
# from mqtt_client import setup_mqtt, video_frames
#
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust as necessary
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# SPRING_BOOT_URL = "http://localhost:8080/user/id"
# user_token = None  # 전역 변수로 토큰을 저장
#
#
# async def fetch_user_id(token: str):
#     headers = {"Authorization": f"Bearer {token}"}
#     async with httpx.AsyncClient() as client:
#         response = await client.get(SPRING_BOOT_URL, headers=headers)
#         response.raise_for_status()
#         return response.json()
#
# async def current_userId(token: str):
#     user_id = await fetch_user_id(token)
#     return user_id
#
# async def get_token(authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid token format")
#     return authorization[7:]  # "Bearer " 이후의 부분만 추출
#
# @app.get("/test-user-id")
# async def test_user_id(token: str = Depends(get_token)):
#     user_id = await current_userId(token)
#     return {"user_id": user_id}
#
# # 프론트엔드에서 JWT 토큰을 받는 엔드포인트
# class TokenRequest(BaseModel):
#     token: str
#
# @app.post("/set-token")
# async def set_token(token_request: TokenRequest):
#     global user_token
#     user_token = token_request.token
#     return {"message": "Token received"}
#
# @app.on_event("startup")
# async def startup_event():
#     global user_token
#     if not user_token:
#         print("No token provided")
#         return
#
#     await setup_mqtt()
#
#     user_id = await current_userId(user_token)
#     print(f"Fetched User ID: {user_id}")
#
#     await fetch_family_photos(user_id)
#
#     asyncio.create_task(recognize_periodically(video_frames, user_id))
#
# if __name__ == "__main__":
#     import uvicorn
#     config = uvicorn.Config(app, host='0.0.0.0', port=8000)
#     server = uvicorn.Server(config)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(server.serve())

import os
import httpx
import asyncio
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from face_image_db import fetch_family_photos
from face_recognition import recognize_periodically
from mqtt_client import setup_mqtt, video_frames
from video_processing import generate_frames, video_frame_generator
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPRING_BOOT_URL = "http://localhost:8080/user/id"
user_token = None  # 전역 변수로 토큰을 저장

async def fetch_user_id(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(SPRING_BOOT_URL, headers=headers)
        response.raise_for_status()
        return response.json()

async def current_userId(token: str):
    user_id = await fetch_user_id(token)
    return user_id

# 프론트엔드에서 JWT 토큰을 받는 엔드포인트
class TokenRequest(BaseModel):
    token: str

@app.post("/set-token")
async def set_token(token_request: TokenRequest):
    global user_token
    user_token = token_request.token
    await initialize_recognition()  # 토큰 설정 후 인식 초기화 작업 실행
    return {"message": "Token received"}

async def initialize_recognition():
    if not user_token:
        print("No token provided")
        return

    await setup_mqtt()

    user_id = await current_userId(user_token)
    print(f"Fetched User ID: {user_id}")

    fetch_family_photos(user_id)

    asyncio.create_task(recognize_periodically(video_frames, user_id))



@app.get("/video")
async def video_stream():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get("/video_feed/{face}")
async def get_video_feed(face: bool):
    return StreamingResponse(video_frame_generator(face),
                             media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
