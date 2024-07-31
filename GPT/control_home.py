# 스마트홈 장치 제어 함수

def control_led(action):
    if action == "켜줘":
        print("LED 조명을 켭니다.")
    elif action == "꺼줘":
        print("LED 조명을 끕니다.")

def control_induction(action):
    if action == "꺼줘":
        print("인덕션을 끕니다.")

def control_air_conditioner(action):
    if action == "켜줘":
        print("에어컨을 켭니다.")
    elif action == "꺼줘":
        print("에어컨을 끕니다.")
