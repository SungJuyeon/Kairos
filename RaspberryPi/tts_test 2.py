import pyttsx3

# 텍스트를 인자로 받아서 음성으로 출력해주는 함수
def text_to_audio(text, lang='ko'):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.yuna')
    engine.say(text)
    engine.runAndWait()

# 그 함수를 실행
text_to_audio("안녕하세요, 이것은 테스트입니다.")

