import os
import pygame
import speech_recognition as sr
from gtts import gTTS



def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening... Please speak into the microphone.")
        try:
            # Adjust the timeout and phrase_time_limit
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language='ko')
            print("[User] " + text)
            return text
        except sr.UnknownValueError:
            #print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            #print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

def speak(text):
    print(text)
    from mqtt_client import text_to_audio
    text_to_audio(text)
    print("발행 완료")