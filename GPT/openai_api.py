import openai
import os
from dotenv import load_dotenv
from weather_info import get_weather_info

# secret API 키를 가져오기 위해 .env file 로드
load_dotenv()

# API key
openai.api_key = os.getenv("GPT_API_KEY")

# AI에게 역할을 부여
messages = [
    {"role": "system", "content": (
        "Your name is Herobot and you are a personal assistant AI. "
        "Your tasks are, first, to inform me of the weather in Seoul. "
        "Second, you act as a calendar assistant."
    )}
]

# 날씨 관련 질문은 weather_info.py 함수 이용
def determine_forecast_day(user_input):
    if "오늘" in user_input or "today" in user_input:
        return 0
    elif "내일" in user_input or "tomorrow" in user_input:
        return 1
    elif "모레" in user_input:
        return 2
    else:
        return None


while True:
    # 사용자에게 질문을 받음
    user_content = input("user: ")

    # forecast day
    forecast_day = determine_forecast_day(user_content)
    if forecast_day is not None:
        weather_info = get_weather_info(forecast_day)
        print(f"assistant: {weather_info}")
        continue

    # 사용자 메시지 저장
    messages.append({"role": "user", "content": user_content})

    # GPT model 생성
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )

    # gpt 답변을 assistant 에 저장
    ai_message = completion.choices[0].message["content"].strip()
    messages.append({"role": "assistant", "content": ai_message})

    # gpt 답변 출력
    print(f"assistant: {ai_message}")

    # exit , bye 를 입력하면 대화 끝
    if user_content.lower() in ['exit', 'bye']:
        print("! bye !")
        break
