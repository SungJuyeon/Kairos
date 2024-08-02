import os

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # 마이크의 샘플 레이트 확인
        sample_rate = source.SAMPLE_RATE
        print(f"Using sample rate: {sample_rate}")

        print("Listening... Please speak into the microphone.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='ko')
        print("[User] " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")


def speak(text):
    print(f"assistant: {text}")
    tts = gTTS(text=text, lang='ko')
    if os.path.exists('assistant.mp3'): #음성 파일이 존재한다면
        os.remove('assistant.mp3') #원래 있던 파일 지우기
    tts.save("assistant.mp3")
    playsound("assistant.mp3")

